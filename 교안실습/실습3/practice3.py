"""
작성자 : 광주_3반_손서현
작성목적 : Pandas EDA, Polars Lazy, DuckDB SQL 비교 실습 목적
작성일 : 2026-07-21

프로그램 설명 : sales_100k.csv를 Pandas·Polars Lazy·DuckDB SQL로 각각 동일하게 집계하고 세 도구의 실행 속도를 비교하는 프로그램

변경사항 내역 (날짜, 변경목적, 변경내용 순으로 기입)
"""
import timeit

import duckdb
import pandas as pd
import polars as pl

# Pandas EDA 기초 탐색
df = pd.read_csv('sales_100k.csv')
df.info()  # 타입·결측·메모리 확인
print(df.isnull().sum())  # 결측치 출력

# IQR 방법으로 이상치 범위 계산 (amount 기준)
Q1 = df['amount'].quantile(0.25)
Q3 = df['amount'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR

print(f"이상치 제거 전 행 수: {len(df)}")
# 이상치 처리
df_clean = df[df['amount'].between(lower, upper)]   # IQR 기준 정상 범위
print(f"이상치 제거 후 행 수: {len(df_clean)}")


# Pandas 집계
pandas_result = (
    df_clean.groupby(['region', 'category'])
    .agg(total=('amount', 'sum'), mean=('amount', 'mean'), count=('amount', 'count'))
    .sort_values('total', ascending=False)  # 총매출 내림차순 정렬
)
print(pandas_result)


# Polars Lazy API로 위와 동일한 집계 작성
polars_result = (
    pl.scan_csv('sales_100k.csv')
    .filter(pl.col('amount').is_between(lower, upper))
    .group_by(['region', 'category'])
    .agg([
        pl.col('amount').sum().alias('total'),
        pl.col('amount').mean().alias('mean'),
        pl.col('amount').count().alias('count'),
    ])
    .sort('total', descending=True)
    .collect()
)
print(polars_result)


# DuckDB SQL로 동일 집계 작성
con = duckdb.connect()
duckdb_result = con.execute(f"""
    SELECT region, category,
           SUM(amount) AS total,
           AVG(amount) AS mean,
           COUNT(amount) AS count
    FROM read_csv_auto('sales_100k.csv')
    WHERE amount BETWEEN {lower} AND {upper}
    GROUP BY region, category
    ORDER BY total DESC
""").df()
print(duckdb_result)


# 세 도구 성능 비교
def run_pandas():
    # polars/duckdb와 동일하게 매번 CSV 읽기부터 다시 수행해야 공정 비교
    d = pd.read_csv('sales_100k.csv')
    d_clean = d[d['amount'].between(lower, upper)]
    d_clean.groupby(['region', 'category']).agg(
        total=('amount', 'sum'), mean=('amount', 'mean'), count=('amount', 'count')
    ).sort_values('total', ascending=False)


def run_polars():
    pl.scan_csv('sales_100k.csv').filter(pl.col('amount').is_between(lower, upper)).group_by(
        ['region', 'category']
    ).agg([
        pl.col('amount').sum().alias('total'),
        pl.col('amount').mean().alias('mean'),
        pl.col('amount').count().alias('count'),
    ]).sort('total', descending=True).collect()


def run_duckdb():
    con.execute(f"""
        SELECT region, category,
               SUM(amount) AS total,
               AVG(amount) AS mean,
               COUNT(amount) AS count
        FROM read_csv_auto('sales_100k.csv')
        WHERE amount BETWEEN {lower} AND {upper}
        GROUP BY region, category
        ORDER BY total DESC
    """).df()


pandas_time = timeit.timeit(run_pandas, number=3)
polars_time = timeit.timeit(run_polars, number=3)
duckdb_time = timeit.timeit(run_duckdb, number=3)

print(f"Pandas: {pandas_time:.4f}초")
print(f"Polars: {polars_time:.4f}초")
print(f"DuckDB: {duckdb_time:.4f}초")
