'''
Step 5.
집계 2. pivot_table - 교차표
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# 총 매출 계산해서 amount 컬럼으로 추가
df['amount'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])

# groupby가 세로 요약이라면, pivot_table은 가로세로 교차표
# 카테고리(세로) × 지역(가로) 교차표로 만들어서 각 조합의 판매액 합계 표시
pivot = df.pivot_table(
    index='category',   # 세로축
    columns='region',   # 가로축
    values='amount',
    aggfunc='sum',
    fill_value=0,   # 빈 칸은 0으로
)

print(pivot)