from repositories.product_repository import ProductRepository
from enum import Enum
from typing import Optional
from jamo import h2j
import json
import jellyfish
from jarowinkler import jarowinkler_similarity
from konlpy.tag import Okt
import re

product_repository = ProductRepository()
okt = Okt()

def split_korean_compound(keyword: str) -> list:
    return re.findall(r'..|.', keyword)

def contains_kyword(keyword_parts: list, product_name: str) -> bool:
    for keyword in keyword_parts:
        if keyword in product_name:
            return True
    return False

def levenstein_distance(s1: str, s2: str) -> int:

    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(m + 1):
        dp[i][0] = i
    
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1) :
        for j in range(1, n+1):
            if s1[i-1] == s2[j-1]:
                dp[i][j] = dp[i-1][j-1]
            else :
                dp[i][j] = 1 + min(dp[i-1][j-1], dp[i-1][j], dp[i][j-1])
    
    return dp[m][n]

def find_similar_keywords(keyword: str, data: list, threshold: float = 1):
    keyword = keyword.rstrip()
    similar_list = []
    for item in data:
        if not item["productName"] :
            continue

        score = levenstein_distance(h2j(keyword), h2j(item["productName"]))
        if score <= threshold :
            item["_score"]= score
            print("점수 : ", score, "상품명 : ", item["productName"])
            similar_list.append(item)
            continue

    similar_list.sort(key=lambda x: x["_score"], reverse=False)
    return similar_list

def find_keywords(keyword: str, data: list, lang: str, threshold: float = 1):
    print("검색어 : ", keyword)
    keyword = keyword.rstrip()
    keyword_parts = okt.nouns(keyword)
    print("검색어 분리 후  : ", keyword_parts)

    similar_list = []
    include_list = []
    sub_include_list = []
    include_ids = set()

    for item in data:
        name = item.get("productName" if lang == "ko" else "productNameEng", "")

        if not name:
            continue

        item_id = id(item)
        name_lower = name.lower()
        keyword_lower = keyword.lower()
        
        # 완전포함
        if keyword_lower in name_lower:
            include_list.append(item)
            include_ids.add(item_id)
            continue

        # 부분 포함
        if lang == "ko" and any(part in name_lower for part in keyword_parts):
            sub_include_list.append(item)
            include_ids.add(item_id)
            continue
        
        # 유사비교
        if item_id not in include_ids:
            if lang == "ko":
                score = levenstein_distance(h2j(keyword), h2j(name))
            else:
                score = levenstein_distance(keyword_lower, name_lower)
            
            if score <= threshold:
                item["_score"] = score
                print("점수 : ", score, "상품명 : ", name)
                similar_list.append(item)

    similar_list.sort(key=lambda x: x["_score"], reverse=False)
    for item in similar_list:
        item.pop("_score", None)
        
    return include_list + sub_include_list+ similar_list

class ProductService:
    def get_all_trademark_data(self, order: str, page: int = 1, limit: int = 10):
        start = (page - 1) * limit
        end = start + limit

        data = product_repository.load_data()
        
        if order == "asc":
            data = sorted(data, key=lambda x: (x.get("productName") is None, x.get("productName", "")))
        elif order == "desc":
            data = sorted(data, key=lambda x: (x.get("productName") is None, x.get("producName", "")), reverse=True)
            
        return data[start: end]
    
    def get_similar_trademark_data(self, q: Optional[str] = None, page: int = 1, limit: int = 10):
        start = (page - 1) * limit
        end = start + limit
        data = product_repository.load_data()

        if q and q.rstrip():
            data = find_similar_keywords(q, data)
        
        return data[start: end]

    def get_search_trademark_data(
        self,
        q: Optional[str] = None,
        status: Optional[str] = None,
        mainCode: Optional[str] = None,
        lang: Optional[str] = "ko",
        page: int = 1,
        limit: int = 10
    ):
        start = (page - 1) * limit
        end = start + limit
        data = product_repository.load_data()

        # 상품 주 분류 코드 필터링
        if mainCode:
            data = [
                item for item in data
                if item["asignProductMainCodeList"] and mainCode in item.get("asignProductMainCodeList", [])
            ]

        # 상표현황 필터링
        if status:
            data = [item for item in data if item["registerStatus"] == status]

        # 상표명 검색 필터링 - 한글, 영어 혼합 검색
        if q and q.rstrip():
            data = find_keywords(q, data, lang)
        
        
        return data[start: end]