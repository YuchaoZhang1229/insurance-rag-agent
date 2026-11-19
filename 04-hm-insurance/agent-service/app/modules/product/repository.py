"""
数据库的 crud 操作
"""
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.product.models import Products
from app.core.logging import get_logger

logger = get_logger(__name__)

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    """ 需求1：查询产品列表 """
    async def find_by_category(self, category: str | None) -> list[Products]:
        # 1.组装查询条件
        # 1.1.默认只查询active状态的产品
        conditions = [Products.status == "active"]
        # 1.2.如果有category，则添加category过滤
        if category:
            conditions.append(Products.category == category)

        # 2.查询产品列表
        query = select(Products).where(*conditions).order_by(Products.id.asc())
        products = (await self.db.scalars(query)).all()
        return products

    """ 需求2：查询推荐候选产品 """
    async def find_limited_by_category(
            self,
            category: str,
            premium_min: Decimal | None,
            limit: int,
    ) -> list[Products]:
        conditions = [
            Products.status == "active",
            Products.category == category,
        ]
        if premium_min is not None:
            conditions.append(Products.min_premium < premium_min)

        products = await self.db.scalars(
            select(Products)
            .where(*conditions)
            .order_by(
                Products.min_premium.asc().nullslast(),
                Products.id.asc(),
            )
            .limit(limit)
        )
        return products.all()
