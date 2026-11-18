"""
数据库表映射类
"""
from uuid import UUID, uuid4
from sqlalchemy import String, BigInteger
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.common.models import Base, CreateAtMixin, UpdateAtMixin

class ChatThreads(Base, CreateAtMixin, UpdateAtMixin):
    __tablename__ = 'chat_threads'

    # 创建索引或注释
    __table_args__ = (
        {"comment": "用户与智能客服的会话元数据，消息正文由 LangGraph Checkpointer 保存"}
    )

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4, comment="会话主键, 同时作为 LangGraph 的 thread_id")
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="JWT 中解析出的业务用户主键，用户标记会话属于哪个用户")
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="新会话", server_default="新会话", comment="会话列表展示标题")
    # created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="会话创建时间")
    # updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="最后一次对话或修改标题的时间")