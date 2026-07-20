'''
Step 2.
범위·제약 조건 추가 — Field()
'''

# Field(): 타입 검사만으로 부족한 범위/조건 등 추가 제약을 값 자리에 선언하는 함수
from pydantic import BaseModel, Field
from typing import Annotated

class Product(BaseModel):
    id: int
    name: str
    price: float = Field(gt=0) # gt = greater than 0 (양수)
    quantity: int = Field(ge=0, le=10000) # 0 이상 10000 이하

# gt(초과) ge(이상) lt(미만) le(이하)