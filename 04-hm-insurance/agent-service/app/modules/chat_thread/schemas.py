"""
请求、响应数据约束
"""

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, field_validator

class ChatThreadRequest(BaseModel):
    title: str = Field(default="新会话", min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        # 字段校验器：在 Pydantic 内置校验之前（mode="before"）执行
        # 作用：去除标题首尾的空白字符（空格、换行、制表符等）
        # 说明：
        #   1. 先做 strip 处理，避免仅含空白字符的标题通过 min_length 校验
        #   2. strip 后的结果会继续参与后续的 min_length / max_length 校验
        return value.strip() # 去除首尾空格

class ChatThreadResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # 允许从其他对象（ORM、普通类）属性中取值
    )