import json

def filter_invalid_data(data: list):
    filtered_data = []
    removed_data = []

    for item in data:
        reasons = []

        if not item.get("productName") and not item.get("productNameEng"):
            reasons.append("상품명(한글)과 상품명(영문)이 모두 비어있음")
        elif not item.get("asignProductMainCodeList") :
            reasons.append("상품 주분류코드리스트가 비어있음")
        elif not item.get("applicationNumber") and not item.get("applicationDate"):
            reasons.append("출원번호(일자)가 비어있음") 
        elif item.get("registerStatus") == "등록" and (not item.get("registrationNumber") or not item.get("publicationNumber")):
            reasons.append("등록상태가 '등록'이고 등록번호 또는 공고번호가 비어있음")
        elif item.get("registerStatus") == "실효" and (not item.get
        ("registrationNumber") or not item.get("publicationNumber")):    
            reasons.append("등록상태가 '실효'이고 등록번호 또는 공고번호가 비어있음")
        elif item.get("registerStatus") == "거절" and (item.get("registrationNumber") or item.get("publicationNumber")):
            reasons.append("등록상태가 '거절'이고 등록번호 또는 공고번호가 있음")
        elif item.get("registerStatus") == "출원" and (item.get("registrationNumber") or item.get("publicationNumber")):
            reasons.append("등록상태가 '출원'이고 등록번호 또는 공고번호가 있음")

        if reasons:
            removed_data.append({
                "item": {
                    "productName": item.get("productName"),
                    "productNameEng": item.get("productNameEng"),
                    "registerStatus": item.get("registerStatus"),
                    "applicationNumber": item.get("applicationNumber"),
                },
                "reasons": reasons
            })
            continue
            
        filtered_data.append(item)
    
    for log in removed_data:
        print("결측 데이터 발견:", log["item"]["productName"], log["item"]["productNameEng"], log["item"]["registerStatus"], log["item"]["applicationNumber"])

    return filtered_data

class ProductRepository:
    def load_data(self):
        with open("trademark_sample.json", "r") as f:
            data = json.load(f)

        filterd_data = filter_invalid_data(data)

        return filterd_data