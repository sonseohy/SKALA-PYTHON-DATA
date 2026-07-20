'''
Step 1.
가장 단순한 모델 하나 만들기 (필드 2개만)
'''

# BaseModel: 상속받으면 타입 힌트대로 값이 맞는지 자동으로 검사해주는 클래스
from pydantic import BaseModel

# Product: id는 정수, name은 문자열이어야 하는 상품 검증 모델
class Product(BaseModel):
    id: int
    name: str

# 값이 타입에 맞는지 검사하며 정상 데이터가 있는 Product 객체 생성
p = Product(id=1, name='사과')
print(p)

# 잘못된 데이터 → ValidationError 발생
try:
    Product(id='숫자아님', name='사과') # id에 문자열을 넣어서 타입 에러 발생시킴
except Exception as e:  # 에러가 나면 프로그램을 멈추지 않고 여기로 넘어와 에러 내용 출력하고 계속 진행
    print('걸림!', e)