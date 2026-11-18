"""
业务逻辑开发
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.modules.chat_thread.repository import ChatThreadRepository
from app.modules.chat_thread.models import ChatThreads

logger = get_logger(__name__)


class ChatThreadService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ChatThreadRepository(session)

    """ 需求1：创建会话 """
    async def create_chat_thread(self, user_id: int, title: str) -> ChatThreads:
        # 用上下文管理，开启事务，运行完成，自动commit，出现异常，自动rollback
        async with self.session.begin():
            chat_thread = ChatThreads(user_id=user_id, title=title)
            await self.repository.add(chat_thread)
            return chat_thread
