'''
질의:
"purchase 또는 refund인 행만 골라서,
event_type별로 묶고,
건수와 amount 평균을 구한 뒤,
건수 내림차순으로 정렬한다"
'''

import time

import duckdb
import pandas as pd
import polars as pl

CSV_PATH = 'events_large.csv'

# Pandas 기준선
start = time.perf_counter()
df = pd.read_csv(CSV_PATH)

res_pandas = (
    df[(df['event_type'] == 'purchase') | (df['event_type'] == 'refund')]
    .groupby('event_type')
    .agg(
        cnt=('amount', 'count'),
        avg=('amount', 'mean')
    )
    .sort_values('cnt', ascending=False)
    .reset_index()
)
t_pandas = (time.perf_counter() - start) * 1000
print(f'Pandas: {t_pandas:.0f} ms')
print(res_pandas.head())

# Polars Lazy 버전
start = time.perf_counter()

res_polars = (
    pl.scan_csv(CSV_PATH)  # scan은 계획만 세움, 실제 실행은 collect에서 일어남
    .filter(pl.col('event_type').is_in(['purchase', 'refund']))
    .group_by('event_type')
    .agg([
        pl.len().alias('cnt'),
        pl.col('amount').mean().alias('avg')
    ])
    .sort('cnt', descending=True)
    .collect()
)
t_polars = (time.perf_counter() - start) * 1000
print(f'Polars: {t_polars:.0f} ms')
print(res_polars)

# DuckDB 버전
start = time.perf_counter()
res_duck = duckdb.sql(f"""
    SELECT event_type,
        COUNT(*) AS cnt,
        AVG(amount) AS avg
    FROM '{CSV_PATH}'
    WHERE event_type IN ('purchase', 'refund')
    GROUP BY event_type
    ORDER BY cnt DESC
""").df()
t_duck = (time.perf_counter() - start) * 1000
print(f'DuckDB: {t_duck:.0f} ms')
print(res_duck)

# 엔진마다 정렬/타입/컬럼 순서가 달라서, 비교 전에 맞춰줘야 한다 (안 맞추면 무조건 실패)
a = res_pandas.sort_values('event_type').reset_index(drop=True)
b = res_polars.to_pandas().sort_values('event_type').reset_index(drop=True)
c = res_duck.sort_values('event_type').reset_index(drop=True)

# atol: 부동소수점 연산 방식이 달라 생기는 미세한 오차를 허용
pd.testing.assert_frame_equal(a, b, check_dtype=False, atol=1e-6)
pd.testing.assert_frame_equal(a, c, check_dtype=False, atol=1e-6)
print('세 엔진 결과 일치!')

# 벤치마크 표로 정리
results = [
    ('Polars', t_polars),
    ('DuckDB', t_duck),
    ('Pandas', t_pandas),
]

base = t_pandas
print(f"{'엔진':<10}{'시간(ms)':>10}{'배속':>10}")
for name, t in sorted(results, key=lambda x: x[1]):
    print(f"{name:<10}{t:>10.0f}{base/t:>9.1f}x")
