import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings                           # 配置管理
from app.core.logging import configure_logging, get_logger     # 日志管理
from contextlib import asynccontextmanager                     # 数据库连接池管理
from app.core.exceptions import register_exception_handlers    # 异常处理注册
from app.modules.product.router import product_router
from app.modules.chat_thread.router import chat_thread_router
from app.modules.chat.router import chat_router


# 初始化日志系统
configure_logging(settings.logging.level)
logger = get_logger(__name__)

# 生命周期管理
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
        app.state.insurance_agent = init_insurance_agent(checkpointer) # 后续可以通过 request.app.state.insurance_agent 获取
        yield
    finally:
        logger.info("应用关闭中... ")
        # 3. 关闭 checkpointer 连接池
        await close_checkpointer()
        # 4. 关闭 SQLAlchemy 连接池
        await close_database()

# 初始化 FastAPI
app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan,
)

# 跨域资源共享（CORS）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # 允许访问的源
    allow_credentials=True,   # 允许携带 Cookie
    allow_methods=["*"],      # 允许所有 HTTP 请求方法
    allow_headers=["*"],      # 允许所有请求头
)

# 路由注册
app.include_router(product_router)
app.include_router(chat_thread_router)
app.include_router(chat_router)

# 全局异常处理注册
register_exception_handlers(app)




@app.get("/health", summary="健康检测接口")
async def health_check() -> dict[str, str]:
    logger.info("执行健康检查")
    return {"status": "ok"}


if __name__ == "__main__":
    import sys
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False,
        loop="asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto",
    )