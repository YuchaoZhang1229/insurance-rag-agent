"""
校验请求参数，返回响应结果
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph.state import CompiledStateGraph

from app.agents.insurance_agent import get_insurance_agent
from app.infra.database import get_db
from app.modules.chat.service import ChatService
from app.modules.chat.schemas import ChatRequest

from app.core.logging import get_logger
logger = get_logger(__name__)

chat_router = APIRouter(prefix="/api/v1/chat", tags=["与AI对话接口"])

def get_chat_service(
        session: AsyncSession = Depends(get_db),
        agent: CompiledStateGraph = Depends(get_insurance_agent)
    ):
    return ChatService(session, agent)

""" 需求1：基本对话 """
@chat_router.post("/")
async def chat(
        user_input: ChatRequest,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatService = Depends(get_chat_service)
    ):
    logger.info(f"基本对话：thread_id：{user_input.thread_id}, message_in：{user_input.message}")
    ai_message = await service.chat(user_input.thread_id, user_id, user_input.message)
    return ai_message