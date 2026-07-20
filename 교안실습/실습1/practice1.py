# ---------------------------------------------
# 작성자 : 손서현
# 작성목적 : 자료구조 집계, 컴프리헨션, 제너레이터 실습 목적
# 작성일 : 2026-07-20
#
# 프로그램 설명 : Sales 데이터를 컴프리헨션/defaultdict/Counter/제너레이터로 집계 분석하고 조건 검증
#
# 변경사항 내역 (날짜, 변경목적, 변경내용 순으로 기입)
#
# ---------------------------------------------

# 1) 리스트/딕셔너리 컴프리헨션
import json
from pathlib import Path    # 파일 경로를 객체로 다루는 라이브러리

# JSON 파일 로드
# Path(): 파일 경로를 Path 객체로 생성
content = Path('Python_Practice2_Data.json').read_text()    # read_text(): 파일을 텍스트로 읽기ㄴ
data = json.loads(content)  # JSON 파싱

# 1. amount >= 1000인 거래 필터링
filtering = [item for item in data if item['amount'] >= 1000]

# 필터링 확인
# print(filtering)

# 2. 지역별 총 매출 dict를 컴프리헨션으로 계산
# set으로 지역명만 중복 제거해 가져와서  
total_sales = {region: sum(item['amount'] for item in data if item['region'] == region) 
          for region in set(item['region'] for item in data)}

print("지역별 총 매출:", total_sales)


# 2) Counter + defaultdict
from collections import Counter, defaultdict

# Counter로 지역별 거래 건수
region_transaction_count = Counter(item['region'] for item in data) # Counter 객체 반환
print("지역별 거래 건수:", region_transaction_count)

# defaultdict로 카테고리별 amount 리스트
category_amounts = defaultdict(list)    # 빈 defaultdict 생성 (없는 키는 빈 리스트 생성)
for item in data:
    category_amounts[item['category']].append(item['amount'])

print("카테고리별 amount 리스트", dict(category_amounts))


# 3) 제너레이터 - 메모리 비교
import sys

# 제너레이터: amount > 1000인 행만 yield
def filter_high_amount(data):
    for item in data:
        if item['amount'] > 1000:
            yield item

# 제너레이터 생성
gen = filter_high_amount(data)

# 리스트 버전
list_ver = [item for item in data if item['amount'] > 1000]

# 메모리 크기 비교
print(f"제너레이터 크기: {sys.getsizeof(gen)} bytes")
print(f"리스트 크기: {sys.getsizeof(list_ver)} bytes")
print(f"차이: {sys.getsizeof(list_ver) - sys.getsizeof(gen)} bytes")


# 4) 종합 - 월별 카테고리 매출 집계

# defaultdict로 month·category별 매출 누적
grouped = defaultdict(int)
for item in data:
    grouped[(item['month'], item['category'])] += item['amount']

# 컴프리헨션으로 dict 변환
result = {key: sales for key, sales in grouped.items()}

print("총매출:", result)