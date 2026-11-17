import uvicorn
from fastapi import FastAPI
from app.core.config import settings                           # 配置管理
from app.core.logging import configure_logging, get_logger     # 日志管理
from contextlib import asynccontextmanager                     # 数据库连接池管理
from fastapi.middleware.cors import CORSMiddleware

# 初始化日志系统
configure_logging(settings.logging.level)
logger = get_logger(__name__)

# 数据库连接池 - 生命周期管理（预留）
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"【{settings.app.name}】应用启动中...")
    from app.infra.database import check_database, close_database
    try:
        # 初始化
        await check_database()
        yield
    finally:
        # 关闭
        logger.info("应用关闭中... ")
        await close_database()

# 初始化 FastAPI
app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan,
)

@app.get("/health", summary="健康检测接口")
async def health_check() -> dict[str, str]:
    logger.info("执行健康检查")
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.app.host,
        port=settings.app.port,
        reload=False
    )