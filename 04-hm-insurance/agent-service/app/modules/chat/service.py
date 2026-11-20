"""
业务逻辑开发
"""
from uuid import UUID
from langchain.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.sse import ServerSentEvent
from app.modules.chat.schemas import ChatRequest
from app.modules.chat_thread.repository import ChatThreadRepository
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError

from app.core.logging import get_logger
logger = get_logger(__name__)


class ChatService:
    def __init__(self, session: AsyncSession, agent: CompiledStateGraph):
        self.repository = ChatThreadRepository(session)
        self.agent = agent

    """ 需求1：阻塞对话 """
    async def chat(self, user_id: int, chat_request: ChatRequest):
        # 判断会话是否存在，且是否属于当前用户
        chat_thread = await self.repository.find_by_thread_id(chat_request.thread_id)
        if not chat_thread or chat_thread.user_id != user_id:
            raise ChatThreadNotFoundError

        config = {"configurable": {"thread_id": chat_request.thread_id}}
        response = await self.agent.ainvoke(
            {"messages": [HumanMessage(content=chat_request.message)]},
            config=config,
        )

        # for message in response["messages"]:
        #     logger.info(f"response: {message.pretty_print()}")

        ai_message = response["messages"][-1]

        logger.info(f"response: {ai_message.pretty_print()}")
        return ai_message.content

    """ 需求2：流式对话 """
    async def chat_stream(self, user_id: int, chat_request: ChatRequest):
        # 判断会话是否存在，且是否属于当前用户
        chat_thread = await self.repository.find_by_thread_id(chat_request.thread_id)
        if not chat_thread or chat_thread.user_id != user_id:
            raise ChatThreadNotFoundError

        config = {"configurable": {"thread_id": chat_request.thread_id}}
        stream = await self.agent.astream_events(
            {"messages": [HumanMessage(content=chat_request.message)]},
            config=config,
            version="v3"
        )

        async for message in stream.messages:
            async for ai_message in message.text:
                yield ServerSentEvent(data=ai_message, event="message")
        yield ServerSentEvent(data="[DONE]", event="done")


