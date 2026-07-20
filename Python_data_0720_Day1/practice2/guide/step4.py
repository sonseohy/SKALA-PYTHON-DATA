'''
Step 4.
중첩 구조 — 모델 안에 모델
'''

from pydantic import BaseModel, Field
from typing import List

class Seller(BaseModel): # 판매자 정보를 검증하는 모델 (안쪽 상자)
    seller_id: int
    region: str

class Product(BaseModel): # 상품 정보를 검증하는 모델 (바깥 상자)
    id: int
    price: float = Field(gt=0)
    seller: Seller # 타입 자리에 다른 모델 사용 (seller 필드는 Seller 타입)
    # 리스트도 각 원소까지 검사됨
    tags: List[str] = [] # 문자열 리스트 타입, 입력 안 하면 빈 리스트가 기본값

# seller에 딕셔너리를 넣으면 Pydantic이 자동으로 Seller 객체로 변환+검증함
p = Product(id=1, price=100, seller={'seller_id': 9, 'region': 'KR'})
print(p.seller.region)  # p 안에 들어있는 Seller 객체 안의 region 값 ('KR')
