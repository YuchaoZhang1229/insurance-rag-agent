"""
校验请求参数，返回响应结果
"""
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.core.logging import get_logger
from app.modules.chat_thread.service import ChatThreadService
from app.modules.chat_thread.schemas import ChatThreadCreate, ChatThreadResponse

logger = get_logger(__name__)
chat_thread_router = APIRouter(prefix="/api/v1/chat-threads")



def get_service(session: AsyncSession = Depends(get_db)):
    return ChatThreadService(session)

""" 需求1：创建会话 """
@chat_thread_router.post("/", response_model=ChatThreadResponse)
async def create_chat_thread(
        user_input: ChatThreadCreate,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
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
        service: ChatThreadService = Depends(get_service)
) -> ChatThreadResponse:
    logger.info(f"查询会话列表，用户ID：{user_id}")
    chat_threads = await service.list_chat_threads(user_id)
    res = [ChatThreadResponse.model_validate(chat_thread) for chat_thread in chat_threads]
    logger.info(f"获取产品类别，结果：{res}")
    return res

""" 需求3：重命名会话 """
@chat_thread_router.patch("/{thread_id}", response_model = ChatThreadResponse)
async def rename_chat_threads(
        thread_id: UUID,
        user_id: Annotated[int, Header(alias="x-user-id")],
        user_input: ChatThreadCreate,
        service: ChatThreadService = Depends(get_service)
) -> ChatThreadResponse:
    chat_thread = await service.rename_chat_threads(thread_id, user_id, user_input.title)
    return ChatThreadResponse.model_validate(chat_thread)