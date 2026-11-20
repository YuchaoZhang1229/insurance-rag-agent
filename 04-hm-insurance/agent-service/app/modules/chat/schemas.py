"""
请求、响应数据约束
"""
from uuid import UUID
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    thread_id: UUID = Field(..., description="通过会话管理接口创建的会话ID")
    message: str = Field(..., description="用户本轮发送的消息")


