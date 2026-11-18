from __future__ import annotations
import logging
import sys
from typing import Any
import structlog

# ===== 新增：颜色常量 =====
_RESET = "\033[0m"
_LOGGER_COLOR = "\033[36m"   # 青色，用于 [logger] 名
# ===== 新增结束 =====

# ===== 新增：把 logger 名移到消息前面 =====
def _move_logger_name_to_event(logger, method_name, event_dict: dict) -> dict:
    """把 logger 名移到消息前面，只给 logger 名上色。"""
    logger_name = event_dict.pop("logger", None) or event_dict.pop("logger_name", None)
    event = event_dict.get("event", "")
    if logger_name:
        # 只给 [logger] 名加颜色，消息正文保持原样
        event_dict["event"] = f"{_LOGGER_COLOR}[{logger_name}]{_RESET} {event}"
    return event_dict
# ===== 新增结束 =====


def configure_logging(level: str = "INFO") -> None:
    """配置彩色控制台日志。"""

    log_level = _log_level(level)

    # 配置 Python 标准 logging
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(
        logging.Formatter("%(message)s")
    )

    root_logger.addHandler(console_handler)

    # 配置 structlog
    processors: list[Any] = [
        # 合并 request_id、conversation_id 等上下文变量
        structlog.contextvars.merge_contextvars,
        # 添加 Logger 名称
        structlog.stdlib.add_logger_name,
        # 添加日志级别
        structlog.stdlib.add_log_level,
        # 添加时间
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
        # 允许添加占位符参数
        structlog.stdlib.PositionalArgumentsFormatter(),
        # 渲染 stack_info=True
        structlog.processors.StackInfoRenderer(),
        # 渲染异常堆栈
        structlog.processors.format_exc_info,
        # ===== 新增开始 =====
        _move_logger_name_to_event,
        # ===== 新增结束 =====
        # 彩色控制台渲染
        structlog.dev.ConsoleRenderer(colors=True),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # 控制第三方库日志数量
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO
        if log_level == logging.DEBUG
        else logging.WARNING
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """获取 structlog 日志器。"""
    return structlog.get_logger(name)

def _log_level(level: str) -> int:
    """将字符串日志级别转换为 logging 常量。"""
    return getattr(logging, level.strip().upper(), logging.INFO)