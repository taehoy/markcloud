# API 사용법 및 실행 방법
## 초기 세팅 및 가상환경 세팅
1. 폴더를 clone한 후, 터미널에서 `python3 -m venv venv` 실행
2. `source venv/bin/activate`을 입력하여 venv 가상환경 실행
3. `pip install -r requirements.txt` 을 입력하여 필요한 모든 가상환경을 설치한다.
4. `uvicorn main:app --reload`을 입력하여 서버 실행

## API 엔드포인트
1. 전체 상표 데이터 조회
    - GET /
    - 쿼리 파라미터
      - order : "asc"(기본값) or "desc"
      - page : 페이지번호 (기본값 = 1)
      - limit : 페이지 당 상표 수 (기본값 = 10)
    ```
    GET /?order=desc&page=2&limit=10 
    ```

2. 상표 검색 API
   - GET /search
   - 쿼리 파라미터
     - q : 검색어(상품명)
     - status : 상표 등록상태 (출원, 등록, 실효, 거절)
     - mainCode : 상표 주분류 코드
     - lang : "ko"(기본값) 또는 "en"
     - page = 페이지번호 (기본값 = 1)
     - limit : 페이지 당 상표 수(기본값 = 10)
    ```
    GET /search?q=바다
    ```
    한글 검색일 경우 형태소 분석을 통해 유사 검색이 가능하며, 자모 단위 유사도 계산을 통해 철자 오차가 있어도 검색됩니다.

쿼리 파라미터는 기본값을 설정하여 선택으로 원하는 결과를 얻을 수 있습니다.

# 구현된 기능 설명
## 상표 전체 조회 (GET /)
- 등록된 모든 상표 데이터를 페이지 단위로 조회합니다.
- order 파라미터를 통해 상품명을 기준으로 오름차순(asc) 또는 내림차순(desc)을 선택하여 정렬할 수 있습니다.
- 정렬 시 상품명이 비어 있는 데이터는 마지막에 정렬됩니다.
- page, limit 파라미터로 페이지네이션을 지원합니다.
  
## 상표 검색 API (GET /search)
- 검색어(q), 등록상태(status), 상품 주분류코드(mainCode),를 기준으로 상표 데이터를 검색할 수 있습니다.
- 상품명(한글)과 상품명(영어) 검색을 모두 지원하며, lang=ko 또는 lang=en으로 설정할 수 있습니다.
- 검색 알고리즘은 다음과 같은 단계로 진행됩니다.
  - 완전 포함 : 검색어가 상품명에 완전히 포함되는 경우
  - 부분 포함 : 한국어인 경우 형태소 분석기를 이용하여 검색어를 분리 후 부분 포함 여부 확인 (OKT 형태소 분석기 사용)
  - 유사어 탐색 : 검색어와 상품명 간 자모 분해 후 levenstein distance 기반 유사도 비교 수행

## 데이터 결측치 처리
- ProductRepository 클래스에서 원본 JSON 데이터를 불러온 뒤, 다음 기준을 만족하지 않는 데이터를 제거합니다.
  - 상품명(한글/영문) 모두 비어있는 경우
  - 상품 주분류 코드가 비어있는 경우
  - 출원번호와 출원일자가 모두 비어있는 경우
  - 들록, 실효 상태에서 등록번호 또는 공고번호가 없는 경우
  - 거절, 출원 상태에서 등록번호 또는 공고번호가 존재하는 경우
- 결측 데이터는 로그로 출력되어 디버깅에 도움을 줍니다.

## 데이터 클렌징
- 모든 API 응답 데이터는 null 값을 빈 문자열로 치환하여 반환됩니다.(`utils.clean_nulls` 함수 활용)

# 기술적 의사결정에 대한 설명
## 1. FastAPI 프레임워크 
- 크래프톤 정글에서는 Flask 프레임워크를 사용하여 개발했다. 과제에서는 FastAPI를 사용했는데 어떤 이유로 FastAPI를 선택했는지 궁금하여 찾아보았다.
- FastAPI 선택 이유
  - 비동기 처리 지원 : 대량의 데이터 요청 및 병렬 처리를 고려했을 때, async 지원이 필요하다.
  - Swagger 자동 문서화 : API 테스트 및 프론트엔드와 협업 시 편의성이 증가한다.

## 2. 레이어드 아키텍처 적용 (Router -> Service -> Repository)
- 처음에 main으로 전부 처리했으나, 코드양이 늘어나면서 가독성이 떨어지고, 한 함수가 모든 로직을 처리하는 것이 효율성이 떨어질 것 같아 아키텍처를 적용했다.
- 레이어드 아키텍처 선택 이유
  - 역할 분리 
    - 라우터는 요청을 받고 비즈니스 로직은 서비스, 데이터 접근은 레포지토리가 담당함으로써 각 계층의 책임을 명확히 했다.
  - 유지보수 용이성
    - 로직 또는 데이터 접근이 바뀌더라도 라우터나 다른 계층에 영향이 적다.

## 3. 서비스 객체에 대한 생성자 주입 
- 기존에는 라우터 내부에서 직접 ProductService()를 생성했다. 이 방식은 결합도가 높고, 리팩토링 시 문제가 발생할 수 있다.
- 따라서 FastAPI의 Depends()와 의존성 주입 함수를 사용하여 개선했다.
```python
def get_product_service():
    repository = ProductRepository()
    return ProductService(repository)
```
- Depends()를 사용함으로써 얻은 장점
  - 클래스 인스턴스를 외부에서 주입 가능하다.
  - 구조의 유연성을 증가시킨다. 스프링의 DI 컨테이너처럼 컨테이너 기반 DI 프레임워크로 확장이 가능하다.
  - SRP(단일 책임 원칙)을 준수한다.

## 4. 검색 기능 : 형태소 분석 + 자모 분해 + levenstein distance
- 단순 부분 문자열 검색만으로는 철자 오타나 띄어쓰기 처리 등 검색이 제대로 동작하지 않았다.

- 따라서 아래와 같은 기술을 이용하여 유사 검색 기능을 구현했습니다.
  - konlpy의 OKT 분석기를 사용하여 한글 명사 추출
  - jamo.h2j()를 통해 한글 문자열을 자모 단위로 분해
  - levenstein distance 알고리즘을 이용하여 오타 및 유사 단어 검색 지원
  
### 문자열 유사도 거리 계산 알고리즘 : levenstein distance
- 여러 문자열 유사도 거리 계산 알고리즘이 존재했고 상표 검색에 적합한 알고리즘을 찾기 위해 고민을 했다.
- 삽입, 삭제, 치환 연산으로 최소 거리를 계산하는 `levenstein distance`가 가장 적합하다고 판단했다.
- 그 전에, 대표적으로 아래 5가지 알고리즘을 비교해보았다.
```
Levenshtein distance(edit distance)
Damerau-Levenshtein distance 
Longest common subsequence 
Hamming distance 
Jaro-Winkler distance
```
- 각 알고리즘의 특징과 왜 사용하지 않았는지 소거법을 통해 결정하였다.
- **Damerau-Levenshtein distance**
    - `Levenshtein distance`에 전치가 추가된 방법이다. 정확도가 높으나 10만개 이상의 상표를 비교하기에는 구현이 복잡하다는 판단이 들었다. 즉, 오버스펙이라고 생각이 들었다.
- **Longest common subsequence** 
    - 순서를 유지하면서 공통 부분 문자열 길이를 계산하는것. 
    - 즉, 오타가 발생할 경우, 순서가 정확히 일치하지 않게되어 유사도를 제대로 판단하지 못할 수 있다고 판단했다. 그리고 길이만 도출하기 때문에 얼마나 유사한지는 직접 계산해야하는 번거로움이 존재했다.
- **Hamming distance**
    - 동일 길이 문자열에서 다른 문자 수를 계산한다. 이는 연산이 빠르나 상표명들의 길이가 다르므로 사용이 불가하다고 판단했다.
- **Jaro-Winkler distance**
  - 알고리즘 선택에 있어서 끝까지 고민한 알고리즘이다.
  - **문자의 순서와 위치를 기반으로 유사도를 측정**한다.
  - 실제 적용해본 결과, "간호사 타이쿤"을 찾기위해 "타이컨"을 입력한 결과, 제대로된 결과가 나오지 않는 것을 확인했다.
  - 이는 해당 알고리즘이 초반 몇 글자가 일치할수록 점수를 높게 주는 방식으로 뒷 부분이 유사하더라도 점수가 낮게 나와 유사도 정확성이 현저히 떨어졌다.
  - 검색 결과 유사도 점수 : 0.7에서 99%정도가 일치한다고 나와있으나 그 미만의 유사도가 나왔다.
  - 한글 검색의 경우, 한글 자모 단위로 비교해서 문자 위치가 아닌 전체 형태가 얼마나 유사한지 판단해야한다. 해당 알고리즘은 순서도 포함되기에 잘못된 유사도가 도출될 것이라 판단했다.


# 문제 해결 과정에서 고민했던 점
## 한글, 영어 모두 뒷단어 검색 시 조회 안되는 현상 발생
현상 
- 처음 `jaro-winkler` 알고리즘을 이용하여 유사 검색을 구현했다. 하지만, 뒷부분이 일치하거나 유사하더라도 제대로 검색되지 않는 현상이 발생했다.

원인
- `jaro-winkler distance`는 두 문자열의 처음부터 비교하므로 뒷부분이 유사하더라도 유사도가 낮게 나와 조회가 되지 않았다.
  
떠올린 해결 방법
- `포함하는 것을 먼저 리스트업하고, 유사 알고리즘을 통해 추후 리스트업하면 뒷부분 일치하는 것도 포함할 수 있겠다.` 판단.
- `continue를 이용하면 모든 데이터의 유사도를 판단하지 않아도 되겠다.` 판단.
  
구현코드
```python
def find_similar_keywords(keyword: str, data: list, lang: str, threshold: float = 0.7):
    
    similar_list = []
    include_list = []
    include_ids = set()
    score = 0.0
    keyword = keyword.rstrip()

    if lang == "ko":
        for item in data:
            if not item["productName"] :
                continue
            if keyword in item["productName"]:
                include_list.append(item)
                include_ids.add(id(item))
                continue

            score = jellyfish.jaro_winkler_similarity(h2j(keyword), h2j(item["productName"]))
            if score >= threshold and id(item) not in include_ids:
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

            score = jellyfish.jaro_winkler_similarity(keyword, item["productNameEng"])
            if score >= threshold and id(item) not in include_ids:
                print("점수 : ", score, "상품명 : ", item["productNameEng"])
                similar_list.append(item)
    
    similar_list.sort(key=lambda x: x["_score"], reverse=True)

    return include_list + similar_list

```

- 뒷 부분의 포함관계 및 출력 순서를 해결했다. 하지만 뒷부분의 유사도를 여전히 처리할 수 없는 문제가 존재했다.

- 유사도 문제를 해결하기위해 순서와 상관없는 알고리즘을 찾기시작했고 그 중 `Levenshtein distance`을 적용시켜보았다.
- 형태소 분석을 위해 h2j를 적용시켜  뒷 부분을 검색해도 유사한 값이 출력되는 걸 확인할 수 있었다.

Levenshtein distance 구현 코드
```python
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
```
Levenshtein distance 적용코드   
```python
 if lang == "ko":
    score = levenstein_distance(h2j(keyword), h2j(name))
else:
    score = levenstein_distance(keyword_lower, name_lower)

if score <= threshold:
    item["_score"] = score
    similar_list.append(item)
```

# 개선하고 싶은 부분
1. 검색 성능 향상을 위한 방법 고려
    - 현재 검색은 순차 탐색인데, 매 요청마다 JSON 데이터를 로드하고 필터링한다. 이는 데이터가 커질수록 성능이 저하된다.
    - Elasticsearch를 활용한 검색이나 JSON 데이터를 redis에 캐싱하는 방법 등을 고려할 수 있다.

2. 서비스 객체에 대한 DI 컨테이너 고려
    - 현재는 Depends()를 이용하여 의존성을 주입하지만, 여러 서비스가 생길 경우 의존성 주입 컨테이너를 도입할 필요가 있다. 

3. 테스트 코드 도입
    - 테스트 코드가 없는 상태로 주요 기능 변경이나 리팩터링 시 동작에 오류가 발생할 수 있음. 
    - 단위 테스트, 통합 테스트, 엣지 케이스 테스트를 도입할 필요가 있다. 