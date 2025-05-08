from fastapi import APIRouter,Query
from enum import Enum
from typing import Optional

from services.product_service import ProductService
from utils.utils import clean_nulls

ProductRouter = APIRouter()
product_service = ProductService()

class RegisterStatus(str, Enum):
    APPLICATION = "출원",
    REGISTRATION = "등록",
    INVALIDATION = "실효",
    REJECTION = "거절"

@ProductRouter.get("/")
async def root(order: str = "asc", page: int = 1, limit: int = 10):
    data = product_service.get_all_trademark_data(order, page, limit)
    result = [clean_nulls(item) for item in data]

    return result

@ProductRouter.get("/similar")
async def similar_search(
    q: Optional[str] = Query(None),
    page: int = 1,
    limit: int = 10
):
    data = product_service.get_similar_trademark_data(q=q, page=page, limit=limit)
    
    result = [clean_nulls(item) for item in data]

    return result


@ProductRouter.get("/search")
async def search(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    mainCode: Optional[str] = Query(None),
    lang: Optional[str] = Query("ko"),
    page: int = 1,
    limit: int = 10
    ):

    data = product_service.get_search_trademark_data(
        q=q,
        status=status,
        mainCode=mainCode,
        lang=lang,
        page=page,
        limit=limit
    )

    result = [clean_nulls(item) for item in data]

    return result