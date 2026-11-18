"""
校验请求参数，返回响应结果
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.core.logging import get_logger
from app.modules.product.service import ProductService
from app.modules.product.schemas import ProductResponse

logger = get_logger(__name__)
product_router = APIRouter(prefix="/api/v1/products")

""" 需求1：查询产品列表 """
@product_router.get("/", response_model=list[ProductResponse])
async def get_products(category: str | None = None, db: AsyncSession = Depends(get_db)) -> list[ProductResponse]:
    service = ProductService(db)
    logger.info(f"获取产品列表，类别：{category}")
    products = await service.list_products(category)
    res = [ProductResponse.model_validate(product) for product in products]
    logger.info(f"获取产品类别，结果：{res}")
    return res
