import asyncio
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "time-mcp": {
            "transport": "stdio",  # 通信方式，可选值有stdio、http或者streamable_http
            "command": "uvx",      # 基于uv(python的uv工具)的包管理工具，用于下载和运行MCP服务
            "args":[               # 运行MCP服务的参数
                "mcp-server-time",
                "--local-timezone=Asia/Shanghai"
            ]
        }
    }
)

model = init_chat_model(
    model = "deepseek-v4-flash",
    extra_body={"thinking": {"type": "disabled"}}
)

async def main():
    tools = await client.get_tools()
    print("获取到的工具：")
    for tool in tools:
        print("-------------------")
        print(f"tool.name: {tool.name}")
        print(f"tool.description: {tool.description}")
        # print(f"tool.args_schema: {tool.args_schema}")
        # print(f"tool.args: {tool.args}")
        print("-------------------")
    agent = create_agent(model, tools)
    response = await agent.ainvoke({
        "messages": [HumanMessage("现在几点了?")]
    })
    for message in response["messages"]:
        message.pretty_print()

if __name__ == "__main__":
    asyncio.run(main())

