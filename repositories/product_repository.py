import json

class ProductRepository:
    def load_data(self):
        with open("trademark_sample.json", "r") as f:
            data = json.load(f)

        # 상품명 필터링 - 상품명과 상품명 영문명이 모두 비어있는 경우
        for item in data:
            if (item["productName"] == "" or not item["productName"]) and  (item["productNameEng"] == "" or not item["productNameEng"]):
                data.remove(item)
        
        # 상품 주분류코드리스트가 비어있는 경우 -> 현재 없음
        for item in data:
            if len(item["asignProductMainCodeList"]) == 0:
                # print(item["asignProductMainCodeList"])
                data.remove(item)

        # 출원번호(일자) 필터링 - 출원번호(일자)가 비어있는 경우 -> 현재 없음
        for item in data:
            if (item["applicationNumber"] == "" or not item["applicationNumber"]) and (item["applicationDate"] == "" or not item["applicationDate"]):
                # print(item["applicationNumber"], item["applicationDate"])
                data.remove(item)
        
        # 상표 등록상태가 "등록"인 경우, 등록번호, 공고번호가 비어있는 경우
        for item in data:
            if item["registerStatus"] == "등록" and ((item["registrationNumber"] == "" or not item["registrationNumber"]) or (item["publicationNumber"] == "" or not item["publicationNumber"])):
                # print(item["registerStatus"], item["registrationNumber"], item["publicationNumber"])
                data.remove(item)

        # 상표 등록상태가 "실효"인 경우, 등록번호 또는 공고번호가 없는 경우
        for item in data:
            if item["registerStatus"] == "실효" and ((item["registrationNumber"] == "" or not item["registrationNumber"]) or (item["publicationNumber"] == "" or not item["publicationNumber"])):
                # print(item["registerStatus"], item["registrationNumber"], item["publicationNumber"])
                data.remove(item)

        # 상표 등록상태가 "거절"인 경우, 등록번호 또는 공고번호가 있는 경우
        for item in data: 
            if item["registerStatus"] == "거절" and (item["registrationNumber"] or item["publicationNumber"]):
                # print(item["registerStatus"], item.get("registrationNumber"), item.get("publicationNumber"))
                data.remove(item)

        # 상표 등록상태가 "출원"인 경우, 등록번호 또는 공고번호가 있는 경우 -> 현재 없음
        for item in data: 
            if item["registerStatus"] == "출원" and (item["registrationNumber"] or item["publicationNumber"]):
                # print("결측 데이터 발견:", item["registerStatus"], item.get("registrationNumber"), item.get("publicationNumber"))
                data.remove(item) 
        return data
