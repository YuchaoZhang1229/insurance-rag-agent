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
    from app.agents.insurance_agent import init_insurance_agent
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