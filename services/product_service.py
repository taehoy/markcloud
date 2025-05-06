from enum import Enum
from typing import Optional
import json

class ProductService:
    def get_all_trademark_data(self, page: int = 1, limit: int = 10):
        start = (page - 1) * limit
        end = start + limit
        with open("trademark_sample.json", "r") as f:
            data = json.load(f)
        return data[start: end]
    
    def get_search_trademark_data(
        self,
        q: Optional[str] = None,
        status: Optional[str] = None,
        order: Optional[str] = "desc",
        mainCode: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ):
        start = (page - 1) * limit
        end = start + limit
        with open("trademark_sample.json", "r") as f:
            data = json.load(f)
        
        # 출원일 정렬 필터링 - 기본값 desc(내림차순)
        if order:
            if order == "asc":
                data = sorted(data, key=lambda x: x["applicationDate"])
            elif order == "desc":
                data = sorted(data, key=lambda x: x["applicationDate"], reverse=True)
        
        # 상품 주 분류 코드 필터링
        if mainCode:
            data = [
                item for item in data
                if item["asignProductMainCodeList"] and mainCode in item.get("asignProductMainCodeList", [])
            ]

        # 상표현황 필터링
        if status:
            data = [item for item in data if item["registerStatus"] == status]

        # 상표명 검색 필터링
        if q and q.rstrip():
            data = [item for item in data if q.lower() in str(item["productName"])]
            
        return data[start: end]