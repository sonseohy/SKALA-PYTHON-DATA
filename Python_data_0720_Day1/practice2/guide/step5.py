'''
Step 5.
40건을 돌리며 유효/무효로 나누기 — 이 실습의 목적지
'''

import json
from pydantic import BaseModel
from pydantic import ValidationError

data = json.load(open('../api_response.json', encoding='utf-8'))['results']

class Product(BaseModel):
    name: str
    category: str

valid, invalid = [], []

for i, row in enumerate(data):
    try:
        # ** : 언팩(unpacking) 연산자, 딕셔너리의 키-값을 함수의 인자로 변환
        # **row : 딕셔너리를 함수 인자로 펼침 (Product(name='Apple', price=100)로 변환)
        valid.append(Product(**row))  # 통과!
    except ValidationError as e:
        invalid.append({
            'index': i,
            'errors': e.errors(),  # 어떤 필드가 왜 불렸는지 (에러 목록)
            'data': row,    # 검증 실패한 원본 데이터
        })