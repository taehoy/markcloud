from fastapi import APIRouter,Query, Depends, HTTPException, status
from enum import Enum
from typing import Optional

from services.product_service import ProductService
from repositories.product_repository import ProductRepository
from utils.utils import clean_nulls
from utils.utils import validate_query

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
    
    if order not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"유효하지 않은 'order' 파라미터 값입니다. 'asc' 또는 'desc'로 입력하시길 바랍니다. 입력한 order 값 : {order}."
            )
    
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

    validate_query(q)
    
    if lang not in ["ko", "en"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"언어 설정(lang)은 'ko'(한글) 또는 'en'(영어)만 지원합니다. 현재 입력한 lang : {lang}. "
        )

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