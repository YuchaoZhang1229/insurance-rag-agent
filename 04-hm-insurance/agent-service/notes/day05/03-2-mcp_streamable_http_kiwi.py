import asyncio
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# 连接Kiwi MCP服务器
client = MultiServerMCPClient(
    {
        "time-mcp": {
            "transport": "stdio",  # 通信方式，可选值有stdio、http或者streamable_http
            "command": "uvx",      # 基于uv(python的uv工具)的包管理工具，用于下载和运行MCP服务
            "args": [  # 运行MCP服务的参数
                "mcp-server-time",
                "--local-timezone=Asia/Shanghai"
            ]
        },
        "kiwi-com-flight-search": {
            "transport": "streamable_http",
            "url": "https://mcp.kiwi.com"
        }
    }
)

model = init_chat_model(
    model = "deepseek-v4-flash",
    extra_body={"thinking": {"type": "disabled"}}
)

async def main():
    tools = await client.get_tools() # 注意MultiServerMCPClient是异步的，结果都是协程对象，需要await
    print("获取到的工具：")
    for tool in tools:
        print(f"tool.name: {tool.name}")
        print(f"tool.description: {tool.description}")
        print("-------------------")
    agent = create_agent(
        model=model,
        tools=tools,
        system_prompt = "You are a travel agent. Help user find best flights. No follow up questions. If the user uses Chinese, use zh-cn as the locale value."
    )
    print("🚀 Starting agent...")
    response = await agent.ainvoke({
        "messages": [HumanMessage("帮我查一下下周四从北京到杭州航班?")]
    })
    for message in response["messages"]:
        message.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())