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

def find_similar_keywords(keyword: str, data: list, lang: str, threshold: float = 2):
    print("검색어 : ", keyword)
    keyword_parts = okt.nouns(keyword)
    print("검색어 분리 후  : ", keyword_parts)

    similar_list = []
    include_list = []
    include_ids = set()
    score = 0.0
    keyword = keyword.rstrip()
    
    if lang == "ko":
        for item in data:

            if not item["productName"] :
                continue

            if contains_kyword(keyword_parts, item["productName"]):
                include_list.append(item)
                include_ids.add(id(item))
                continue
            # for keyword in keyword_parts:
            #     if keyword in item["productName"]:
            #         include_list.append(item)
            #         include_ids.add(id(item))

            # score = jellyfish.jaro_winkler_similarity(h2j(keyword), h2j(item["productName"]))
            # score = jarowinkler_similarity(keyword, item["productName"])
            score = levenstein_distance(h2j(keyword), h2j(item["productName"]))
            if score <= threshold and id(item) not in include_ids:
                item["_score"]= score
                print("점수 : ", score, "상품명 : ", item["productName"])
                similar_list.append(item)

    if lang == "en":
        for item in data:
            if not item["productNameEng"]:
                continue

            if keyword in item["productNameEng"]:
                include_list.append(item)
                include_ids.add(id(item))
                continue

            score = jarowinkler_similarity(h2j(keyword), h2j(item["productNameEng"]))
            if score <= threshold and id(item) not in include_ids:
                print("점수 : ", score, "상품명 : ", item["productNameEng"])
                similar_list.append(item)
    
    similar_list.sort(key=lambda x: x["_score"], reverse=False)
    # for item in similar_list:
    #     item.pop("_score", None)
        
    return include_list + similar_list

class ProductService:
    def get_all_trademark_data(self, page: int = 1, limit: int = 10):
        start = (page - 1) * limit
        end = start + limit

        data = product_repository.load_data()
        
        return data[start: end]
    
    def get_search_trademark_data(
        self,
        q: Optional[str] = None,
        status: Optional[str] = None,
        order: Optional[str] = "desc",
        mainCode: Optional[str] = None,
        lang: Optional[str] = "ko",
        page: int = 1,
        limit: int = 10
    ):
        start = (page - 1) * limit
        end = start + limit
        data = product_repository.load_data()


        # # 출원일 정렬 필터링 - 기본값 desc(내림차순)
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

        # 상표명 검색 필터링 - 한글, 영어 혼합 검색
        if q and q.rstrip():
            data = find_similar_keywords(q, data, lang)
        
        
        return data[start: end]