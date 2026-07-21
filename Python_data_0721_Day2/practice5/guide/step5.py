'''
Step 5.
벤치마크 표로 정리
'''
import pandas as pd, time
import polars as pl, time

# step1.py
start = time.perf_counter()
df = pd.read_csv('../events_large.csv')

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

# step2.py
start = time.perf_counter()

res_polars = (
    pl.scan_csv('../events_large.csv')
    .filter(pl.col('event_type').is_in(['purchase', 'refund']))
    .group_by('event_type')
    .agg([
        pl.len().alias('cnt'),
        pl.col('amount').mean().alias('avg')
    ])
    .sort('cnt', descending=True)
    .collect()
    #.explain()
)

t_polars = (time.perf_counter() - start) * 1000

# step3.py

import duckdb, time

start = time.perf_counter()
res_duck = duckdb.sql("""
    SELECT event_type,
        COUNT(*) AS cnt,
        AVG(amount) AS avg
    FROM '../events_large.csv'
    WHERE event_type IN ('purchase', 'refund')
    GROUP BY event_type
    ORDER BY cnt DESC
""").df()

t_duck = (time.perf_counter() - start) * 1000


results = [
    ('Polars', t_polars),
    ('DuckDB', t_duck),
    ('Pandas', t_pandas),
]

base = t_pandas
print(f"{'엔진':<10}{'시간(ms)':>10}{'배속':>10}")
for name, t in sorted(results, key=lambda x: x[1]):
    print(f"{name:<10}{t:>10.0f}{base/t:>9.1f}x")

# 세 엔진의 실행 시간 비교표가 출력되고, Polars < DuckDB < Pandas 순서를 확인함