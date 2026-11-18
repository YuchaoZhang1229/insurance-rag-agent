"""
请求、响应数据约束
"""
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class ProductResponse(BaseModel):
    id: int
    name: str
    clause_name: str
    category: str
    insurer: str
    image_url: str
    description: str
    min_premium: Decimal  | None
    max_premium: Decimal  | None
    target_group: str | None
    highlights: list[str] | None
    status: str

    model_config = ConfigDict(
        from_attributes=True,  # 允许从其他对象（ORM、普通类）属性中取值
    )
