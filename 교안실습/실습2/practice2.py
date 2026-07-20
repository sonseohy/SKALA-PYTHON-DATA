"""
작성자 : 손서현
작성목적 : 파일 I/O, 예외처리, Pydantic 검증 파이프라인 실습 목적
작성일 : 2026-07-20

프로그램 설명 : JSON 파일의 판매 데이터를 Pydantic으로 검증해 유효/무효 데이터를 분리한 후 CSV/JSON으로 저장하고 재검증

변경사항 내역 (날짜, 변경목적, 변경내용 순으로 기입)
"""

import json
import csv
import logging
from typing import Optional
from pydantic import BaseModel, field_validator, ValidationError

# 로거 설정
logger = logging.getLogger('pipeline')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

logger.addHandler(ch)

# 1) 예외 처리 + 파일 읽기
def safe_load_csv(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        logger.info(f"로딩 성공: {len(data)}건")
        return data
    except FileNotFoundError:
        logger.error(f"파일을 찾을 수 없습니다: {filepath}")
        return None
    finally:
        print("로딩 종료")


# 2) Pydantic v2 스키마 정의
class SalesRecord(BaseModel):
    region: str
    month: str
    amount: int
    category: Optional[str] = None   # 없어도 됨

    @field_validator("region", "month")
    @classmethod
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("비어있으면 안 됩니다.")
        return v

    @field_validator("amount")
    @classmethod
    def amount_positive(cls, v):
        if v <= 0:
            raise ValueError("amount는 0보다 커야 합니다.")
        return v


# 3) 검증 파이프라인 (valid/errors 분리)
def validate_records(raw_data):
    valid = []
    errors = []
    for row in raw_data:
        try:
            record = SalesRecord(**row)
            valid.append(record.model_dump())
        except ValidationError as e:
            print(f"검증 오류 발생: {row} -> {e}")   # 오류 내용 출력
            errors.append({"row": row, "error": str(e)})
    return valid, errors


# 4. 결과 저장 + 재로딩 확인
def save_and_reload(valid, errors, csv_path="valid_records.csv", json_path="errors.json"):
    # valid 레코드를 CSV로 저장
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["region", "month", "amount", "category"])
        writer.writeheader()
        writer.writerows(valid)

    # errors를 JSON으로 저장
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(errors, f, ensure_ascii=False, indent=2)

    # 재로딩
    with open(csv_path, encoding="utf-8") as f:
        reloaded_valid = list(csv.DictReader(f))
    with open(json_path, encoding="utf-8") as f:
        reloaded_errors = json.load(f)

    logger.info(f"재로딩 확인: valid {len(reloaded_valid)}건 / errors {len(reloaded_errors)}건")
    return reloaded_valid, reloaded_errors


if __name__ == "__main__":
    none_result = safe_load_csv("존재하지_않는_파일.json")
    assert none_result is None
    print("파일 없음 -> None 반환 통과\n")

    # 확인용 샘플 데이터
    sample_data = [
        {"region": "서울", "month": "2024-01", "amount": 1000},              # valid
        {"region": "부산", "month": "2024-02", "amount": 500, "category": "의류"},  # valid
        {"region": "대구", "month": "2024-03", "amount": 700},               # valid
        {"region": "인천", "month": "2024-04", "amount": 300},               # valid
        {"region": "", "month": "2024-01", "amount": 500},                  # error: region 빈값
        {"region": "부산", "month": "", "amount": 300},                     # error: month 빈값
        {"region": "대구", "month": "2024-02", "amount": -50},              # error: amount <= 0
    ]

    valid, errors = validate_records(sample_data)
    assert len(valid) == 4
    assert len(errors) == 3
    print(f"valid {len(valid)}건 / errors {len(errors)}건 assert 통과\n")

    reloaded_valid, reloaded_errors = save_and_reload(valid, errors)
    assert len(reloaded_valid) == 4
    print(f"재로딩 후 len(reloaded)==4 통과\n")

    print("모든 조건 통과")