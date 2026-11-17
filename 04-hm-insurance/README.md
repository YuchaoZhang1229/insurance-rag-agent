## 部署前端 frontend
放在一个路径不含中文的目录下，然后执行命令，安装依赖，
```shell
npm install
```

再执行命令， 启动前端，通过 http://localhost:5173 访问
```shell
npm run dev
```



## 后端 agent-service 项目搭建，安装依赖

修改pyproject.toml文件，内容如下：
```toml
[project]
name = "agent-service"
version = "0.1.0"
description = "Insurance AI agent service"
requires-python = ">=3.14"
dependencies = [
    "aiostream>=0.7.1",
    "asyncpg>=0.31.0",
    "beautifulsoup4>=4.15.0",
    "dashscope>=1.26.4",
    "fastapi>=0.139.2",
    "ipykernel>=7.3.0",
    "langchain>=1.3.14",
    "langchain-community>=0.4.2",
    "langchain-deepseek>=1.1.0",
    "langchain-mcp-adapters>=0.3.0",
    "langchain-milvus>=0.4.0",
    "langchain-ollama>=1.1.0",
    "langchain-text-splitters>=1.1.2",
    "langgraph-checkpoint-postgres>=3.1.0",
    "mineru-open-sdk>=0.2.5",
    "openai>=2.48.0",
    "psycopg[binary,pool]>=3.3.4",
    "pwdlib[argon2]>=0.3.0",
    "pydantic>=2.13.4",
    "pydantic-settings>=2.14.2",
    "pyjwt>=2.13.0",
    "pymilvus>=3.0.0",
    "pypdf>=6.14.2",
    "sqlalchemy[asyncio]>=2.0.51",
    "structlog>=26.1.0",
    "uvicorn>=0.51.0",
]


[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

执行命令，下载依赖：
```shell
uv sync
```