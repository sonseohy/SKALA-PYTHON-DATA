'''
Step 3.
커스텀 규칙 — field_validator
'''

from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str
    category: str

    # @field_validator('category'): category 필드에 이 검증 함수를 연결하는 데코레이터
    # @classmethod: 인스턴스가 아닌 클래스 자체를 다루는 메서드라는 표시 (field_validator와 짝)
    @field_validator('category')
    @classmethod
    def normalize_category(cls, v: str) -> str:
        v = v.strip().lower()   # 앞뒤 공백 제거 + 전부 소문자로 변환
        if not v:   # 빈 문자열이면
            # raise: 에러를 발생시켜 코드 실행을 즉시 멈추고 try/except가 있으면 그쪽으로 넘김
            # ValueError('메시지'): 에러 내용을 담은 에러 객체 생성
            raise ValueError('category는 비어 있을 수 없습니다')    # 에러 발생
        return v
    
# field_validator는 인스턴스가 만들어지기 전(검증 도중)에 호출됨
# → self(인스턴스) 대신 cls(클래스)를 받아야 하므로 @classmethod가 필수로 짝을 이룸s