# 종합실습 1: 비동기 ETL 파이프라인 (Extract -> Transform -> Load -> Orchestrate)

import asyncio
import time
from pathlib import Path
from typing import Annotated

import pandas as pd
import pytest
from pydantic import BaseModel, Field, ValidationError, field_validator

# 설정값
MAX_CONCURRENT = 5  # 백프레셔: 동시 요청 수 제한
MAX_RETRIES = 3
REQUEST_TIMEOUT = 3.0  # 요청별 타임아웃(초)
FAIL_ONCE_IDS = {5, 12}  # 이 id들은 첫 시도만 일부러 실패시켜 재시도 동작을 시연

BASE_DIR = Path(__file__).parent
OUT_DIR = (
    BASE_DIR / "output"
)  # 산출물(CSV/Parquet)은 소스 옆이 아니라 별도 폴더에 모은다
CSV_PATH = OUT_DIR / "products.csv"
PARQUET_PATH = OUT_DIR / "products.parquet"

# 카테고리별로 묶음(batch)을 만들고, 각 묶음의 정해진 순번(BAD_PRICE_SLOT)에는
# 일부러 음수 가격을 심어 Transform 단계에서 실제로 걸러지는지 확인한다.
# (id 하나하나를 직접 나열하는 대신, 배치 크기와 "몇 번째가 불량인지"만 정의)
CATEGORY_BATCHES = [
    ("gadgets  ", 7),
    ("FURNITURE", 7),
    ("beauty", 6),
    (" Sports", 6),
    ("grocery ", 6),
]
BAD_PRICE_SLOT = 3  # 각 배치에서 이 순번(0부터 시작)의 상품 가격을 오염시킨다


def build_products() -> list[dict]:
    rows = []
    next_id = 0
    for category, batch_size in CATEGORY_BATCHES:
        for slot in range(batch_size):
            is_corrupted = slot == BAD_PRICE_SLOT
            rows.append(
                {
                    "id": next_id,
                    "name": f"상품_{next_id:03d}",
                    "category": category,
                    "price": -1.0 if is_corrupted else round(3000 + next_id * 777.7, 2),
                    "in_stock": slot % 2 == 0,
                }
            )
            next_id += 1
    return rows


RAW_PRODUCTS = build_products()
RAW_BY_ID = {row["id"]: row for row in RAW_PRODUCTS}
TOTAL_ITEMS = len(RAW_PRODUCTS)


# Pydantic 검증 모델: 스키마 정규화 + 가격 규칙을 한 곳에서 강제
class Product(BaseModel):
    id: int
    name: str
    category: str
    price: Annotated[float, Field(ge=0)]  # 음수 가격 거부
    in_stock: bool

    @field_validator("category")
    @classmethod
    def normalize_category(cls, v: str) -> str:
        return v.strip().lower()  # 스키마 정규화: 카테고리 소문자화


# Extract: 비동기 수집 · 동시성 제한 · 재시도
async def fetch_one(item_id: int, attempt_state: dict, sem: asyncio.Semaphore) -> dict:
    async with sem:  # 입장권 없으면 대기 (백프레셔)
        async with asyncio.timeout(REQUEST_TIMEOUT):
            await asyncio.sleep(0.05)  # 네트워크 대기 상황
            if item_id in FAIL_ONCE_IDS and attempt_state.get(item_id, 0) == 0:
                attempt_state[item_id] = 1
                raise ConnectionError(
                    f"{item_id}번 일시적 네트워크 오류"
                )  # 첫 시도만 실패
            return RAW_BY_ID[item_id]


async def fetch_retry(
    item_id: int,
    attempt_state: dict,
    sem: asyncio.Semaphore,
    max_retries: int = MAX_RETRIES,
) -> dict | None:
    for attempt in range(max_retries):
        try:
            return await fetch_one(item_id, attempt_state, sem)
        except TimeoutError:
            if attempt == max_retries - 1:
                return None
        except Exception:
            if attempt == max_retries - 1:  # 마지막 시도까지 실패하면 포기
                return None
            wait = 2**attempt * 0.1  # 지수 백오프: 0.1 -> 0.2 -> 0.4초
            await asyncio.sleep(wait)


async def extract() -> list[dict]:
    # Semaphore는 실행 중인 이벤트 루프에 바인딩되므로, 매번 새 루프에서 새로 만들어야
    # asyncio.run()을 여러 번 호출해도(예: 테스트) 이전 루프에 묶여 깨지지 않는다.
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    attempt_state: dict[int, int] = {}
    tasks = [fetch_retry(row["id"], attempt_state, sem) for row in RAW_PRODUCTS]
    results = await asyncio.gather(*tasks)
    return [r for r in results if r is not None]  # 예외 격리: 끝내 실패한 건은 건너뜀


# Transform: Pydantic 검증 -> 유효/무효 분리
def transform(raw_rows: list[dict]) -> tuple[list[Product], list[dict]]:
    valid: list[Product] = []
    invalid: list[dict] = []
    for row in raw_rows:
        try:
            valid.append(Product(**row))
        except ValidationError as e:
            invalid.append({"data": row, "errors": e.errors()})
    return valid, invalid


# Load: DataFrame -> CSV·Parquet 저장
def load(
    valid_products: list[Product],
    csv_path: Path = CSV_PATH,
    parquet_path: Path = PARQUET_PATH,
) -> pd.DataFrame:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame([p.model_dump() for p in valid_products])
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    df.to_parquet(parquet_path, index=False)
    return df


# Orchestrate: 전체 단계 조율
async def run(
    csv_path: Path = CSV_PATH, parquet_path: Path = PARQUET_PATH
) -> tuple[pd.DataFrame, list[dict]]:
    raw_rows = await extract()
    valid, invalid = transform(raw_rows)
    df = load(valid, csv_path, parquet_path)
    return df, invalid


# 단위 테스트 (pytest -v 로 실행)
def test_category_normalized():
    p = Product(id=1, name="상품", category=" Electronics ", price=1000, in_stock=True)
    assert p.category == "electronics"


def test_price_rejected():
    with pytest.raises(ValidationError):
        Product(id=1, name="상품", category="electronics", price=-100, in_stock=True)


def test_split_counts():
    valid, invalid = transform(RAW_PRODUCTS)
    assert len(valid) + len(invalid) == len(RAW_PRODUCTS)
    assert len(invalid) == len(CATEGORY_BATCHES)  # 배치마다 정확히 1건씩 음수 가격


def test_parquet_roundtrip(tmp_path):
    valid, _ = transform(RAW_PRODUCTS)
    df = load(valid, tmp_path / "out.csv", tmp_path / "out.parquet")
    restored = pd.read_parquet(tmp_path / "out.parquet")
    pd.testing.assert_frame_equal(
        df.reset_index(drop=True), restored.reset_index(drop=True)
    )


def test_retry_works():
    results = asyncio.run(extract())
    ids = {r["id"] for r in results}
    assert FAIL_ONCE_IDS.issubset(ids)  # 첫 시도 실패 건도 재시도 끝에 결국 수집됨


def test_run_pipeline(tmp_path):
    df, invalid = asyncio.run(run(tmp_path / "run.csv", tmp_path / "run.parquet"))
    assert (tmp_path / "run.csv").exists()
    assert (tmp_path / "run.parquet").exists()
    assert len(df) + len(invalid) == len(RAW_PRODUCTS)


# 실행: 수집 -> 검증 -> 적재 -> 결과 출력
if __name__ == "__main__":
    start = time.perf_counter()
    result_df, invalid_rows = asyncio.run(run())
    elapsed = time.perf_counter() - start

    print("=" * 40)
    csv_rel = CSV_PATH.relative_to(BASE_DIR)
    parquet_rel = PARQUET_PATH.relative_to(BASE_DIR)
    print(f"적재 완료: {len(result_df)}건 -> {csv_rel}, {parquet_rel}")
    print(f"무효 데이터: {len(invalid_rows)}건")
    for item in invalid_rows:
        for err in item["errors"]:
            field = ".".join(str(x) for x in err["loc"])
            print(f"  - id={item['data']['id']} {field}: {err['msg']}")
    print(f"처리 시간: {elapsed:.2f}초")
