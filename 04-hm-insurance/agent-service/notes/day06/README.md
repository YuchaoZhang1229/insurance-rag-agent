## 保险顾问 Agent

### 一、学习目标
- 能实现 `PostgreSql` 实现 Agent 短期记忆
- 能利用 `FastAPI` 管理 Agent 生命周期
- 能基于 `SSE` 实现前端的流式对话
- 能利用 `Checkpointer` 实现会话历史管理



### 二、`PostgreSql checkpointer` 初始化， 并由 FastAPI 管理其生命周期
用 `PostgreSql` 实现 `Checkpointer`，将会话状态（即快照链）持久化到数据库中

#### 2.1 安装依赖
```bash
uv add langgraph-checkpoint-postgres "psycopg[binary,pool]"
```
两个依赖的作用如下：
- `langgraph-checkpoint-postgres`：提供 `PostgresSaver` 和 `AsyncPostgresSaver`；
- `psycopg[binary,pool]`：负责连接 `PostgreSQL`，并提供异步连接池支持。

当前项目基于 FastAPI 异步开发，因此后面使用的是 `AsyncPostgresSaver`


#### 2.2 配置数据库连接 `app.core.config.py`
- SQLAlchemy 使用 `asyncpg` 驱动
- PostgreSQL Checkpointer 使用 `psycopg` 驱动

两者访问的是同一个数据库 `insurance`, 但是连接协议不同

| 使用位置 | 连接协议 | 示例 |
|---|---|---|
| SQLAlchemy | `postgresql+asyncpg` | `postgresql+asyncpg://insurance:***@localhost:5432/insurance` |
| PostgreSQL Checkpointer | `postgresql` | `postgresql://insurance:***@localhost:5432/insurance` |

因此，修改 `app.core.config.py` 文件中的 `DatabaseSetting`，先抽取一个创建连接地址的私有方法，再分别定义 `url` 和 `checkpoint_url`

#### 2.3 checkpointer 初始化 `app.infra.checkpointer.py`


#### 2.4 FastAPI 管理 checkpointer 生命周期 `app.main.py`
实现项目启动时初始化 checkpointer，在项目关闭时关闭 checkpointer
```python
# 数据库连接池 - 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"【{settings.app.name}】应用启动中...")
    from app.infra.database import check_database, close_database
    from app.infra.checkpointer import init_checkpointer, close_checkpointer
    try:
        # 1. 检查业务数据库连接
        await check_database()
        # 2. 初始化 checkpointer
        checkpointer = await init_checkpointer()
        yield
    finally:
        logger.info("应用关闭中... ")
        # 3. 关闭 checkpointer 连接池
        await close_checkpointer()
        # 4. 关闭 SQLAlchemy 连接池
        await close_database()
```

#### 2.5 事件循环错误
Windows 下 Psycopg 的异步连接不能运行在 `ProactorEventLoop` 上，必须使用 `SelectorEventLoop`。而当前版本的 Uvicorn 会在 Windows 下显式创建 `ProactorEventLoop`，从而绕过全局事件循环策略。
所以，我们需要在启动 Uvicorn 时，判断当前系统是否是Windows：
- 如果是Windows，直接通过导入字符串 `asyncio:SelectorEventLoop` 指定事件循环类；
- Linux 环境继续使用 Uvicorn 的默认配置即可。

```python
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False,
        loop= "asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto",  # 新增
    )
```

### 三、保险顾问 Agent 初始化， 并由 FastAPI 管理其生命周期

#### 3.1 Agent 初始化 `app.agents.insurance_agent.py`
```python
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.core.config import settings
from app.core.logging import get_logger
logger = get_logger(__name__)


SYSTEM_PROMPT = """
你是“安心保”的智能保险顾问。
你需要使用专业、准确、容易理解的语言回答用户的保险问题。
当信息不足时，应先向用户追问，不要编造保险产品或保障内容。
"""


def init_insurance_agent(checkpointer: AsyncPostgresSaver):
    """初始化保险顾问Agent"""
    # 1.初始化模型
    model = init_chat_model(
        model=settings.llm.chat_model,
        model_provider="deepseek",
        api_key=settings.llm.api_key,
        extra_body={"thinking": {"type": "disabled"}},
    )

    # 2.创建Agent
    agent = create_agent(
        model=model,
        tools=[],
        checkpointer=checkpointer,
        system_prompt=SYSTEM_PROMPT,
    )
    logger.info("保险顾问 Agent 初始化成功~✅️")
    return agent
```

#### 3.2 FastAPI 管理 Agent 生命周期 `app.main.py`

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"【{settings.app.name}】应用启动中...")
    from app.infra.database import check_database, close_database
    from app.infra.checkpointer import init_checkpointer, close_checkpointer
    from app.agents.insurance_advisor_agent import init_insurance_agent
    try:
        # 1. 检查业务数据库连接
        await check_database()
        # 2. 初始化 checkpointer
        checkpointer = await init_checkpointer()
        # 3. 初始化保险顾问 Agent
        app.state.insurance_agent = init_insurance_agent(checkpointer)
        yield
    finally:
        logger.info("应用关闭中... ")
        # 3. 关闭 checkpointer 连接池
        await close_checkpointer()
        # 4. 关闭 SQLAlchemy 连接池
        await close_database()
```

> 说明：
> - `app.state` 是FastAPI的共享状态，用来保存与当前 FastAPI 应用实例共同存在的对象
> - 后面实现对话接口时，可以通过 `request.app.state.agent` 获取这里创建的 Agent，不需要重新初始化

推荐只用依赖注入的方式来获取 agent
```python
# app/deps.py
from fastapi import Request, HTTPException

def get_insurance_agent(request: Request):
    agent = getattr(request.app.state, "insurance_agent", None)
    if agent is None:
        raise HTTPException(503, "Agent 未就绪")
    return agent


# 路由中使用
from fastapi import Depends

@app.post("/chat")
async def chat(agent = Depends(get_insurance_agent)):
    result = await agent.ainvoke(...)
    return result
```

### 四、保险顾问 Agent 基础对话接口实现
https://my.feishu.cn/wiki/YNPIwHSgCimOfUkDpvxcuVpJntd

见 3.1 接口设计

创建会话模块 `app.modules.chat`
- `schemas.py`：定义请求和响应模型
- `service.py`：校验会话并调用 Agent
- `router.py`：定义 HTTP 接口

先试用 `ainvoke()`获取完整回复，验证对话接口，后续再把完整响应改成 SSE 流式响应

### 五、FastAPI SSE 流式对话实现

#### 5.1 什么是 SSE
SSE（**S**erver-**S**ent **E**vents）是一种基于 HTTP 的**服务器向浏览器推送数据**的单向通信技术。浏览器用 `EventSource` API 建立长连接，服务器以 `text/event-stream` 格式持续发送文本事件
- 单向：服务器 → 客户端 ;
- 基于 HTTP/HTTPS，使用 `text/event-stream` 格式
- 浏览器 `EventSource` 原生支持自动重连
- 适合：AI流式输出
- 不适合：高频双向通信，双向通信用 WebSocket 更适合

#### 5.2 SSE数据格式
1. 特定的响应头

| 响应头字段 | 必须值 | 作用说明 |
| :--- | :--- | :--- |
| `Content-Type` | `text/event-stream` | 告诉浏览器这是一个 SSE 数据流 |
| `Cache-Control` | `no-cache` | 禁用缓存，确保数据实时更新 |
| `X-Accel-Buffering`| `no` | **关键避坑**：禁用 Nginx 等反向代理的缓冲，否则流式效果会失效 |<websource>source_group_web_5</websource>

2. 数据帧格式
每个事件由字段组成，字段间用换行符分隔，**事件必须以两个换行符（\n\n）结尾**
```text
data: {"content": "你好"}\n\n
```
- `data`：事件携带的实际数据（通常是 JSON 字符串）。
- `event`：自定义事件类型（可选，前端可通过 addEventListener 监听）。
- `id`：事件 ID，用于断线重连时定位（可选）。
- `retry`：浏览器重连等待时间（毫秒，可选）


#### 5.3 FastAPI 实现 SSE
在 FastAPI 中使用原生 SSE 支持，核心只需两步：
- **声明响应类型**：在路由装饰器中，将 `response_class` 设置为 `EventSourceResponse`。
- **封装返回数据**：在异步生成器中，使用 `ServerSentEvent` 对象封装数据并 `yield` 出去

| 组件 | 来源 | 核心作用                                                                                                        |
| :--- | :--- |:------------------------------------------------------------------------------------------------------------|
| `EventSourceResponse` | `fastapi.sse` | 封装响应类型，继承自 `StreamingResponse`，自动设置 `text/event-stream`、`Cache-Control: no-cache` 和 `X-Accel-Buffering: no` |
| `ServerSentEvent` | `fastapi.sse` | 封装数据格式，支持 `data`、`event`、`id`、`retry` 等标准 SSE 字段                                                            |

`ServerSentEvent` 的结构大概是这样：
```pyhton
class ServerSentEvent(BaseModel):
    id: str
    event: str
    data: str
    retry: int
    # ...
```
只需要我们把结果封装为 `ServerSentEvent` 对象，FastAPI 即可帮我们以 SSE 需要的格式返回

```python
from fastapi.sse import EventSourceResponse, ServerSentEvent

@app.post("", response_class=EventSourceResponse)
async def chat():
    """AI对话接口"""

    # 用一个循环来模拟sse不断返回数据
    for i in range(10):
        yield ServerSentEvent(data=f"message_{i}", event="message")
    yield ServerSentEvent(data="[DONE]", event="done")
```

### 六、利用 `Checkpointer` 实现会话历史管理
我们已经做了会话列表的查询，但是对于当前会话的会话历史查询，我们还没有实现


#### 6.1 读取和删除会话状态
- 见 [01-测试PostgreSQL的Checkpointer.py](01-%E6%B5%8B%E8%AF%95PostgreSQL%E7%9A%84Checkpointer.py)


```python
    # 1. 读取 State 快照 agent.aget_state(config)
    # 获取会话的最新状态，即最后一次完成的会话历史
    snapshot = await agent.aget_state(config)
    print("✅ 会话状态获取成功")
    print(snapshot)

    # 2. 删除快照 checkpointer.adelete_thread(thread_id)
    thread_id = config["configurable"]["thread_id"]
    await checkpointer.adelete_thread(thread_id)


    snapshot = await agent.aget_state(config)
    if snapshot.values == {}:
        print("✅ 会话状态删除成功")
        print(snapshot)
```


#### 接口设计
- [接口设计见 5.2](https://my.feishu.cn/wiki/YNPIwHSgCimOfUkDpvxcuVpJntd)




### 七、定义候选保险产品查询工具
目前保险顾问 Agent 只能依靠大模型自身知识回答问题，无法读取项目数据库中的真实保险产品
- `app.agents.insurance_advisor_agent.py`：负责初始化并组装保险顾问 Agent
- `app.agents.tools.py`：具体工具



```python
from decimal import Decimal
from fastapi.encoders import jsonable_encoder

from langchain_core.tools import tool
from app.modules.product.models import Products
from app.modules.product.service import ProductService
from app.infra.database import AsyncSessionFactory

from app.core.logging import get_logger
logger = get_logger(__name__)



@tool
async def query_candidate_products(
        categories: list[str],
        premium_min: Decimal | None = None,
        limit_per_category: int = 5
    ) -> list[Products]:
    """ 根据险种和保费条件查询可用于推荐的候选保险产品。当用户咨询具体保险产品或需要保险产品推荐时使用。
    Args:
    categories：产品分类列表，可选值为 medical、critical_illness、life、accident。
    premium_min：最低保费上限，可选参数，只返回最低保费小于该值的产品。
    limit_per_category：每个险种最多返回的产品数量，可选参数，默认5。
    """
    logger.info(f"调用查询候选产品工具：categories: {categories}, premium_min: {premium_min}, limit_per_category: {limit_per_category}")
    async with AsyncSessionFactory() as db:
        product_service = ProductService(db)
        products: list[Products] = await product_service.get_candidate_products(categories, premium_min, limit_per_category)
    return jsonable_encoder(products) # 把 list[Products] 转换为 JSON 格式


```



















