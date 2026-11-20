"""
业务逻辑开发
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph.state import CompiledStateGraph
from langchain_core.messages import HumanMessage, AIMessage
from app.modules.chat_thread.repository import ChatThreadRepository
from app.modules.chat_thread.models import ChatThreads
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError
from app.modules.chat_thread.schemas import ChatHistoryResponse, ChatMessageResponse

from app.core.logging import get_logger
logger = get_logger(__name__)


class ChatThreadService:
    def __init__(self, session: AsyncSession, agent: CompiledStateGraph):
        self.session = session
        self.repository = ChatThreadRepository(session)
        self.agent = agent

    """ ====================================会话列表管理==================================== """
    """ 需求1：创建会话 """
    async def create_chat_thread(self, user_id: int, title: str) -> ChatThreads:
        # 用上下文管理，开启事务，运行完成，自动commit，出现异常，自动rollback
        async with self.session.begin():
            chat_thread = ChatThreads(user_id=user_id, title=title)
            await self.repository.add(chat_thread)
            return chat_thread

    """ 需求2：查询会话列表 """
    async def get_chat_threads(self, user_id: int) -> list[ChatThreads]:
        products = await self.repository.find_by_user_id(user_id)
        return products

    """ 需求3：重命名会话 """
    async def rename_chat_thread(self, thread_id: UUID, user_id: int, title: str):
        async with self.session.begin():
            chat_thread = await self.repository.find_by_thread_id(thread_id)

            if not chat_thread or chat_thread.user_id != user_id:
                raise ChatThreadNotFoundError
            chat_thread.title = title # update_at 还不是最新的

            # update_at 字段由数据库生成，需要刷新数据 flush + refresh
            await self.session.flush()
            await self.session.refresh(chat_thread)

            return chat_thread

    """ 需求4：删除会话 """
    async def delete_chat_thread(self, thread_id: UUID, user_id: int):
        # 1. 删除会话列表
        async with self.session.begin():
            chat_thread = await self.repository.find_by_thread_id(thread_id)
            if not chat_thread or chat_thread.user_id != user_id:
                raise ChatThreadNotFoundError
            await self.repository.delete(chat_thread)

        # 2. 删除会话状态
        await self.agent.checkpointer.adelete_thread(str(thread_id))


    """ ================================================================================== """

    """ ====================================会话列表管理==================================== """
    """ 需求1：查询会话状态 """
    async def get_chat_history(self, thread_id: UUID, user_id: int) -> ChatHistoryResponse:
        chat_thread = await self.repository.find_by_thread_id(thread_id)
        if not chat_thread or chat_thread.user_id != user_id:
            raise  ChatThreadNotFoundError

        config = {"configurable": {"thread_id": thread_id}}
        snapshot = await self.agent.aget_state(config) # StateSnapshot对象

        messages = []
        for message in snapshot.values.get("messages", []):
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "assistant"
            else:
                continue

            if message.text:
                messages.append(
                    ChatMessageResponse(
                        role=role,
                        content=message.text,
                    )
                )

        return ChatHistoryResponse(thread_id=thread_id, messages=messages)

    """ 需求2：删除会话状态, 添加到`会话列表管理`的`删除会话`中 """

    """ ================================================================================== """







