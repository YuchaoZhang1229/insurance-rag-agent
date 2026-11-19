"""
数据库的 crud 操作
"""
from uuid import UUID
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

    """ 需求2：查询会话列表 """
    async def find_by_user_id(self, user_id: int) -> list[ChatThreads]:
        query = (
            select(ChatThreads)
            .where(ChatThreads.user_id == user_id)
            .order_by(
                ChatThreads.updated_at.desc(),
                ChatThreads.created_at.desc(),
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    """ 需求3：重命名会话 """
    async def find_by_thread_id(self, thread_id: UUID) -> ChatThreads | None:
        return await self.db.get(ChatThreads, thread_id)