"""
业务逻辑开发
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.modules.chat_thread.repository import ChatThreadRepository
from app.modules.chat_thread.models import ChatThreads
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError

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

    """ 需求2：查询会话列表 """
    async def list_chat_threads(self, user_id: int) -> list[ChatThreads]:
        products = await self.repository.find_by_user_id(user_id)
        return products

    """ 需求3：重命名会话 """
    async def rename_chat_threads(self, thread_id: UUID, user_id: int, title: str):
        logger.info(f"{thread_id}")
        async with self.session.begin():
            chat_thread = await self.repository.find_by_thread_id(thread_id)

            if not chat_thread or chat_thread.user_id != user_id:
                raise ChatThreadNotFoundError
            chat_thread.title = title

            await self.session.refresh(chat_thread)

            return chat_thread