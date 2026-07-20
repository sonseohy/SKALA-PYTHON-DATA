import json
from datetime import date
from typing import Annotated, List

from pydantic import BaseModel, Field, ValidationError, field_validator


# 중첩 모델: profile 딕셔너리를 검증하는 안쪽 상자
class Profile(BaseModel):
    country: str
    tier: str
    score: Annotated[float, Field(ge=0, le=100)]  # 0 이상 100 이하만


# 바깥 모델: 레코드 하나를 검증하는 상자
class User(BaseModel):
    id: int
    username: str
    email: str
    age: Annotated[int, Field(ge=0, le=120)]  # 음수 나이 차단
    is_active: bool
    signup_date: date  # 'YYYY-MM-DD' 문자열을 date로 자동 파싱
    profile: Profile    # profile은 Profile 타입
    tags: List[str] = []

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        # 형식 검사: '@'가 있고, '@' 뒤에 '.'이 있어야 함
        if '@' not in v or '.' not in v.split('@', 1)[1]:
            raise ValueError('올바른 이메일 형식이 아닙니다')
        return v


def main() -> None:
    data = json.load(open('api_response.json', encoding='utf-8'))['results']
    print('전체 건수:', len(data))

    valid, invalid = [], []
    for i, row in enumerate(data):
        try:
            valid.append(User(**row))
        except ValidationError as e:
            invalid.append({
                'index': i,
                'errors': e.errors(),
                'data': row,
            })

    print(f'유효: {len(valid)}건 / 오염(무효): {len(invalid)}건\n')

    print(f"{'행':<4}{'필드':<16}{'사유'}")
    for item in invalid:
        for err in item['errors']:
            field = '.'.join(str(x) for x in err['loc'])  # 중첩 경로 표시 (예: profile.score)
            print(f"{item['index']:<4}{field:<16}{err['msg']}")


if __name__ == '__main__':
    main()
