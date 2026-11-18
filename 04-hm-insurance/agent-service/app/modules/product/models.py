"""
数据库表映射类
"""

from decimal import Decimal
from sqlalchemy import Index, BigInteger, String, Text, Numeric, ARRAY, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.common.models import Base, CreateAtMixin, UpdateAtMixin

""" products 产品表的 ORM 模型 """
class Products(Base, CreateAtMixin, UpdateAtMixin):

    __tablename__ = 'products'

    # 创建索引
    __table_args__ = (
        CheckConstraint("category IN ('medical', 'critical_illness', 'accident', 'life')", name="chk_products_category"),
        Index("idx_products_category", "category"),
        Index("idx_products_status", "status"),
        {"comment": "保险商城在售及历史保险产品"}
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, comment="产品主键")
    name: Mapped[str] = mapped_column(String(200), nullable=False, comment="商城展示名称")
    clause_name: Mapped[str] = mapped_column(String(300), nullable=False, comment="主条款文件名，包含 .pdf 后缀")
    category: Mapped[str] = mapped_column(String(50), nullable=False, comment="险种分类：医疗、重疾、意外或寿险")
    insurer: Mapped[str] = mapped_column(String(120), nullable=False, comment="承保保险公司")

    image_url: Mapped[str | None] = mapped_column(Text, comment="产品展示图片地址")
    description: Mapped[str| None] = mapped_column(Text, comment="产品简介")
    min_premium: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), comment="产品公开的最低年缴保费参考")
    max_premium: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), comment="产品公开的最高保费参考，可为空")
    target_group: Mapped[str| None] = mapped_column(String(300), comment="适用人群说明")
    highlights: Mapped[list[str] | None] = mapped_column(ARRAY(Text), comment="产品亮点列表")
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="active", comment="产品状态")
    # created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), comment="创建时间")
    # updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now(), comment="最后更新时间")

if __name__ == "__main__":
    products = Products(
        id=1,
        name="百万医疗险2026版",
        clause_name="medical_2026.pdf",
        category="medical",
        insurer="平安保险",
        min_premium=Decimal("358.00"),
        max_premium=Decimal("5000.00"),
    )
    print(products)




















