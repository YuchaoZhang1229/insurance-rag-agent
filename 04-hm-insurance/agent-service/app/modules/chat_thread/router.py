"""
校验请求参数，返回响应结果
"""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Header, status, Response
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph.state import CompiledStateGraph
from app.agents.insurance_advisor_agent import get_insurance_agent
from app.infra.database import get_db
from app.core.logging import get_logger
from app.modules.chat_thread.service import ChatThreadService
from app.modules.chat_thread.schemas import ChatThreadCreate, ChatThreadResponse, ChatHistoryResponse

logger = get_logger(__name__)
chat_thread_router = APIRouter(prefix="/api/v1/chat-threads")

def get_chat_thread_service(
        session: AsyncSession = Depends(get_db),
        agent: CompiledStateGraph = Depends(get_insurance_agent)
):
    return ChatThreadService(session, agent)

""" ====================================会话列表管理==================================== """
""" 需求1：创建会话 """
@chat_thread_router.post("/", response_model=ChatThreadResponse)
async def create_chat_thread(
        user_input: ChatThreadCreate,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_chat_thread_service)
) -> ChatThreadResponse:
    logger.info(f"新建会话：用户ID：{user_id}, 会话名称：{user_input.title}")
    res = await service.create_chat_thread(user_id, user_input.title)
    res = ChatThreadResponse.model_validate(res)
    logger.info(f"新建会话：{res}")
    return res

""" 需求2：查询会话列表 """
@chat_thread_router.get("/", response_model=list[ChatThreadResponse])
async def get_chat_threads(
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_chat_thread_service)
) -> list[ChatThreadResponse]:
    logger.info(f"查询会话列表，用户ID：{user_id}")
    chat_threads = await service.get_chat_threads(user_id)
    res = [ChatThreadResponse.model_validate(chat_thread) for chat_thread in chat_threads]
    logger.info(f"获取产品类别，结果：{res}")
    return res

""" 需求3：重命名会话 """
@chat_thread_router.patch("/{thread_id}", response_model = ChatThreadResponse)
async def rename_chat_thread(
        thread_id: UUID,
        user_id: Annotated[int, Header(alias="x-user-id")],
        user_input: ChatThreadCreate,
        service: ChatThreadService = Depends(get_chat_thread_service)
) -> ChatThreadResponse:
    logger.info(f"重命名会话：用户ID：{user_id}, 会话ID：{thread_id}, 新名称：{user_input.title}")
    chat_thread = await service.rename_chat_thread(thread_id, user_id, user_input.title)
    logger.info(f"重命名会话：{chat_thread}")
    return ChatThreadResponse.model_validate(chat_thread)

""" 需求4：删除会话 """
@chat_thread_router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_thread(
        thread_id: UUID,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_chat_thread_service)
) -> Response:
    await service.delete_chat_thread(thread_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
""" ================================================================================== """


""" ====================================会话列表管理==================================== """
""" 需求1：查询会话历史 """
@chat_thread_router.get("/{thread_id}/messages", response_model=ChatHistoryResponse)
async def get_chat_history(
        thread_id: UUID,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_chat_thread_service)
) -> ChatHistoryResponse:
    return  await service.get_chat_history(thread_id, user_id)

""" 需求2：删除会话状态, 添加到`会话列表管理`的`删除会话`中 """

""" ================================================================================== """












