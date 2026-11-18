"""
校验请求参数，返回响应结果
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.core.logging import get_logger
from app.modules.chat_thread.service import ChatThreadService
from app.modules.chat_thread.schemas import ChatThreadRequest, ChatThreadResponse

logger = get_logger(__name__)
chat_thread_router = APIRouter(prefix="/api/v1/chat-threads")



def get_service(session: AsyncSession = Depends(get_db)):
    return ChatThreadService(session)

@chat_thread_router.post("/", response_model=ChatThreadResponse)
async def create_chat_thread(
        user_input: ChatThreadRequest,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatThreadService = Depends(get_service)
) -> ChatThreadResponse:
    logger.info(f"新建会话：用户ID-{user_id}, 会话名称-{user_input.title}")
    res = await service.create_chat_thread(user_id, user_input.title)
    res = ChatThreadResponse.model_validate(res)
    logger.info(f"新建会话：{res}")
    return res