"""
校验请求参数，返回响应结果
"""
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_db
from app.core.logging import get_logger
from app.modules.product.service import ProductService
from app.modules.product.schemas import ProductResponse

logger = get_logger(__name__)
product_router = APIRouter(prefix="/api/v1/products")

def get_product_service(session: AsyncSession = Depends(get_db)):
    return ProductService(session)

""" 需求1：查询产品列表 """
@product_router.get("/", response_model=list[ProductResponse])
async def get_products(
        category: str | None = None,
        service: ProductService = Depends(get_product_service)
) -> list[ProductResponse]:
    logger.info(f"获取产品列表，类别：{category}")
    products = await service.list_products(category)
    res = [ProductResponse.model_validate(product) for product in products]
    logger.info(f"获取产品类别，结果：{res}")
    return res

""" 需求2：查询推荐候选产品 """
@product_router.get("/candidates", response_model = list[ProductResponse])
async def get_candidate_products(
        categories: list[str] = Query(min_length=1),     # 产品类别
        premium_min: Decimal | None = None,              # 只返回最低保费小于该值的产品
        limit_per_category: int = 5,                     # 每个类别最多返回的数量
        service: ProductService = Depends(get_product_service)
) -> list[ProductResponse]:
    logger.info(f"获取候选产品列表")
    products = await service.get_candidate_products(categories, premium_min, limit_per_category)
    res = [ProductResponse.model_validate(product) for product in products]
    logger.info(f"获取候选产品列表，结果：{res}")
    return res
