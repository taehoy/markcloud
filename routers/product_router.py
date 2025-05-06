from fastapi import APIRouter,Query
from enum import Enum
from typing import Optional
from services.product_service import ProductService

import json

ProductRouter = APIRouter()
product_service = ProductService()

class RegisterStatus(str, Enum):
    APPLICATION = "출원",
    REGISTRATION = "등록",
    INVALIDATION = "실효",
    REJECTION = "거절"

@ProductRouter.get("/")
async def root(page: int = 1, limit: int = 10):
    result = product_service.get_all_trademark_data(page, limit)

    return result

@ProductRouter.get("/search")
async def search(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    order: Optional[str] = Query("desc"),
    mainCode: Optional[str] = Query(None),
    page: int = 1,
    limit: int = 10
    ):

    result = product_service.get_search_trademark_data(
        q=q,
        status=status,
        order=order,
        mainCode=mainCode,
        page=page,
        limit=limit
    )
    return result