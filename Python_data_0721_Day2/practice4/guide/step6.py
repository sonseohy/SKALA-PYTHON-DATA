'''
Step 6.
집계 3. merge - 다른 표와 결합
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# 총 매출 계산해서 amount 컬럼으로 추가
df['amount'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])

# other_df 코드로 만들기 (category 이용)
other_df = pd.DataFrame({
    'category': ['Beauty', 'Home'],
    'product_type': ['화장품', '가구'],
    'cost_price': [5000, 80000],
    'supplier': ['Supplier_A', 'Supplier_B']
})

# how를 잘못 고르면 데이터가 조용히 사라진다.
# df의 category와 other_df의 category를 기준으로 merge
merged = df.merge(other_df, on='category', how='left')

'''
how = 'inner' : 양쪽 다 있는 것만 (행이 줄 수 있으니 주의)
how = 'left' : 왼쪽 전부 유지 (기본권장)
how = 'outer' : 양쪽 전부 유지
'''

# merge 후 반드시 행 수 확인
print(len(df), '→', len(merged))

