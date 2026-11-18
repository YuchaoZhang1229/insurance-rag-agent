"""
数据库的 crud 操作
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.product.models import Products
from app.core.logging import get_logger

logger = get_logger(__name__)


""" 需求1：查询产品列表 """
class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_by_category(self, category: str | None = None) -> list[Products]:
        # 1.组装查询条件
        # 1.1.默认只查询active状态的产品
        conditions = [Products.status == "active"]
        # 1.2.如果有category，则添加category过滤
        if category:
            conditions.append(Products.category == category)

        # 2.查询产品列表
        query = select(Products).where(*conditions).order_by(Products.id.asc())
        products = (await self.db.scalars(query)).all()
        logger.info(f"产品列表：{products}")
        return products
