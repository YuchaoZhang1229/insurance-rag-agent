"""
数据库的 crud 操作
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chat_thread.models import ChatThreads
from app.core.logging import get_logger

logger = get_logger(__name__)



class ChatThreadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    """ 需求1：创建会话 """
    async def add(self, chat_thread: ChatThreads):
        self.db.add(chat_thread)
        # commit 操作放到 service 层去做

