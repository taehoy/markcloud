from fastapi import APIRouter,Query, Depends
from enum import Enum
from typing import Optional

from services.product_service import ProductService
from repositories.product_repository import ProductRepository
from utils.utils import clean_nulls

ProductRouter = APIRouter()

#생성자 주입 함수
def get_product_service():
    repository = ProductRepository()
    return ProductService(repository)


class RegisterStatus(str, Enum):
    APPLICATION = "출원",
    REGISTRATION = "등록",
    INVALIDATION = "실효",
    REJECTION = "거절"

@ProductRouter.get("/")
async def root(order: str = "asc",
            page: int = 1,
            limit: int = 10,
            service: ProductService = Depends(get_product_service)
            ):
    data = service.get_all_trademark_data(order, page, limit)
    result = [clean_nulls(item) for item in data]

    return result

@ProductRouter.get("/search")
async def search(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    mainCode: Optional[str] = Query(None),
    lang: Optional[str] = Query("ko"),
    page: int = 1,
    limit: int = 10,
    service: ProductService = Depends(get_product_service)
    ):

    data = service.get_search_trademark_data(
        q=q,
        status=status,
        mainCode=mainCode,
        lang=lang,
        page=page,
        limit=limit
    )

    result = [clean_nulls(item) for item in data]

    return result