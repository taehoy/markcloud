# null 값 -> ""로 변환
def clean_nulls(record: dict) -> dict:
    return {
        k: ("" if v is None else v)
        for k, v in record.items()
    }
