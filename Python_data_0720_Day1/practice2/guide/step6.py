'''
Step 6.
탈락 사유를 표로 출력 (확장 과제)
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
        valid.append(Product(**row))
    except ValidationError as e:
        invalid.append({
            'index': i,
            'errors': e.errors(),
            'data': row,
        })

# '행'을 좌측정렬 4글자 너비로 출력, '필드'를 좌측정렬 12글자 너비로 출력
print(f"{'행':<4}{'필드':<12}{'사유'}")
for item in invalid:
    for err in item['errors']:
        # err['loc']의 각 요소를 문자로 변환하고 '.'으로 연결
        field = '.'.join(str(x) for x in err['loc'])  # 중첩 경로 표시
        print(f"{item['index']:<4}{field:<12}{err['msg']}")