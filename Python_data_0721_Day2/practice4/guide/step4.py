'''
Step 4.
집계 1. groupby.agg - 그룹별 요약
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# 총 매출 계산해서 amount 컬럼으로 추가
df['amount'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])

# 카테고리별로 집계한 후 소수점 첫째자리까지 반올림
summary = df.groupby('category', observed=True).agg(    # 실제로 존재하는 카테고리만 그룹화
    건수=('unit_price', 'count'),
    평균가=('unit_price', 'mean'),
    중앙값=('unit_price', 'median'),
    총매출=('amount', 'sum'),
).round(1)

#print(df.head())    # amount 추가 확인
print(summary)