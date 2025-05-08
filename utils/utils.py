from fastapi import HTTPException
import re
# null 값 -> ""로 변환
def clean_nulls(record: dict) -> dict:
    return {
        k: ("" if v is None else v)
        for k, v in record.items()
    }

def validate_query(q: str):
    q = q.strip()
    if not q:
        raise HTTPException(
            status_code=400,
            detail="검색어가 비어 있습니다."
        )
    if len(q) < 2:
        raise HTTPException(
            status_code=400,
            detail="검색어는 최소 2자 이상이어야 합니다."
        )
    if len(q) > 50:
        raise HTTPException(
            status_code=400,
            detail="검색어는 50자 이하여야 합니다."
        )
    if not re.search(r"[가-힣a-zA-Z0-9]", q):
        raise HTTPException(
            status_code=400,
            detail="검색어에 한글, 영문 또는 숫자가 포함되어야 합니다."
        )
