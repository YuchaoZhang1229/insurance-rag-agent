"""
业务逻辑开发
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logging import get_logger
from app.modules.product.repository import ProductRepository
from app.modules.product.models import Products

logger = get_logger(__name__)


class ProductService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ProductRepository(session)

    async def list_products(self, category: str | None = None) -> list[Products]:
        products = await self.repository.find_by_category(category)
        logger.info(f"产品列表：{products}")
        return products