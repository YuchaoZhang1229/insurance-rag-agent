import sys
import asyncio
# ⚠️ 必须放在文件最顶部，在所有 import 之前
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.core.config import settings
from dotenv import load_dotenv

load_dotenv()

# 创建连接池
checkpoint_pool = AsyncConnectionPool(
    conninfo=settings.db.checkpoint_url,
    min_size=1,  # 池最小连接数
    max_size=5,  # 池最大连接数
    kwargs={
        "autocommit": True,       # 自动提交事务
        "prepare_threshold": 0,   # 不做预准备sql
        "row_factory": dict_row,  # 查询结果以dict返回
    },
    open=False,  # 不自动创建连接, 随后通过 open() 方法手动创建连接
)

async def main():
    # 初始化连接
    await checkpoint_pool.open()
    # 等待连接池就绪
    await checkpoint_pool.wait(timeout=60)
    print("✅ 连接池就绪")

    # 初始化checkpointer
    checkpointer = AsyncPostgresSaver(checkpoint_pool)
    # 自动建表（与checkpointer存储有关的表），该方法具有幂等性，重复执行不会重复创建，因此可以在应用启动时调用
    await checkpointer.setup()
    print("✅ Checkpointer 初始化完成，表已创建")

    from langchain.agents import create_agent
    from langchain.chat_models import init_chat_model
    from langchain_core.messages import HumanMessage

    # 初始化模型
    model = init_chat_model(
        "deepseek-v4-flash",
        extra_body={"thinking": {"type": "disabled"}},
    )
    # 创建Agent
    agent = create_agent(
        model=model,
        tools=[],
        checkpointer=checkpointer,
    )

    config = {"configurable": {"thread_id": "day06-checkpointer-test"}}
    # 第一次，告知自己的信息
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content="我叫小明，今年30岁。")]},
        config=config,
    )
    # 第二次，询问信息
    response = await agent.ainvoke(
        {"messages": [HumanMessage(content="我今年多大？")]},
        config=config,
    )
    for message in response['messages']:
        message.pretty_print()

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

if __name__ == "__main__":
    asyncio.run(main())
