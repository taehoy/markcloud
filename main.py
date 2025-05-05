from fastapi import FastAPI, Query
from enum import Enum
from typing import Optional
import json

app = FastAPI()

class RegisterStatus(str, Enum):
    APPLICATION = "출원",
    REGISTRATION = "등록",
    INVALIDATION = "실효",
    REJECTION = "거절"

@app.get("/")
async def root(page: int = 1, limit: int = 10):
    start = (page - 1) * limit
    end = start + limit
    with open("trademark_sample.json", "r") as f:
        data = json.load(f)
    
    return data[start: end]

@app.get("/search")
async def search(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    page: int = 1,
    limit: int = 10
    ):
    print(q)
    start = (page - 1) * limit
    end = start + limit
    with open("trademark_sample.json", "r") as f:
        data = json.load(f)

    # 상표현황 필터링
    if status:
        data = [item for item in data if item["registerStatus"] == status]

    # 상표명 검색 필터링
    if q and q.rstrip():
        data = [item for item in data if q.lower() in str(item["productName"])]

    return data[start: end]