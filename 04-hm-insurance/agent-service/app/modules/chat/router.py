"""
校验请求参数，返回响应结果
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession
from langgraph.graph.state import CompiledStateGraph

from app.agents.insurance_advisor_agent import get_insurance_agent
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

""" 需求1：阻塞对话 """
@chat_router.post("/test")
async def chat(
        chat_request: ChatRequest,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatService = Depends(get_chat_service)
    ):
    ai_message = await service.chat(user_id, chat_request)
    return ai_message


""" 需求2：流式对话 """
@chat_router.post("/", response_class=EventSourceResponse)
async def chat_stream(
        chat_request: ChatRequest,
        user_id: Annotated[int, Header(alias="x-user-id")],
        service: ChatService = Depends(get_chat_service)
    ):
    # Generator：用 yield 不断生成内容，形成动态列表
    async for ai_message in service.chat_stream(user_id, chat_request):
        yield ai_message
