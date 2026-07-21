'''
Step 4.
결과 일치 검증 - 가장 중요한 단계
'''
import pandas as pd
import polars as pl
import duckdb

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
)

res_duck = duckdb.sql("""
    SELECT event_type,
        COUNT(*) AS cnt,
        AVG(amount) AS avg
    FROM '../events_large.csv'
    WHERE event_type IN ('purchase', 'refund')
    GROUP BY event_type
    ORDER BY cnt DESC
""").df()

# 비교 전 정렬, 타입, 컬럼 순서를 마줘야 한다. (안 맞추면 무조건 실패)
a = res_pandas.sort_values('event_type').reset_index(drop=True)
b = res_polars.to_pandas().sort_values('event_type').reset_index(drop=True)
c = res_duck.sort_values('event_type').reset_index(drop=True)

# pandas vs polars (다르면 AssertionError 발생)
pd.testing.assert_frame_equal(a, b, check_dtype=False, atol=1e-6)
# pandas vs DuckDB (다르면 AssertionError 발생)
pd.testing.assert_frame_equal(a, c, check_dtype=False, atol=1e-6)
print('세 엔진 결과 일치!') # 위의 두 비교 모두 통과해야 실행됨

# atol=1e-6 : 부동소수점은 미세한 오차가 정상이므로 허용 오차를 준다.
