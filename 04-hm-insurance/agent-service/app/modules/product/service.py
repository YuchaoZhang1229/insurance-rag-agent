"""
业务逻辑开发
"""
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.modules.product.repository import ProductRepository
from app.modules.product.models import Products

logger = get_logger(__name__)


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProductRepository(session)

    """ 需求1：查询产品列表 """
    async def list_products(self, category: str | None = None) -> list[Products]:
        products = await self.repository.find_by_category(category)
        return products

    """ 需求2：查询候选产品列表 """
    async def get_candidate_products(
            self,
            categories: list[str],
            premium_min: Decimal | None,
            limit_per_category: int
    ) -> list[Products]:
        candidate_products: list[Products] = []

        for category in dict.fromkeys(categories):
            products = await self.repository.find_limited_by_category(
                category=category,
                premium_min=premium_min,
                limit=limit_per_category,
            )
            candidate_products.extend(products)
        return candidate_products
