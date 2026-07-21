'''
Step 2.
결측 처리 - 그룹별 중앙값 대치
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# 아래 방식으로 하면 X (전체 평균 - 잘못됨)
# df['price'] = df['price'].fillna(df['price'].mean())
# 전체 데이터의 평균으로 모든 NaN을 채움
# 문제: 카테고리 상관없이 다 같은 값으로 채워짐 → 이상치에 끌려감

# 그룹별 중앙값으로 채우기 (전체 평균은 이상치에 왜곡되지만, 그룹별 중앙값은 이상치 영향이 적어서 더 정확한 결측치 보충이 가능)
# transform() : 각 그룹에 함수를 적용하고, 원본 크기를 유지한 결과를 반환 (원래 행 개수를 그대로 유지하면서 각 행에 그룹의 값을 되돌려줌 → fillna에 바로 사용 가능)
# observed=True: category 타입의 컬럼을 groupby할 때, 실제로 존재하는 카테고리만 그룹화하라는 뜻
df['unit_price'] = df.groupby('category', observed=True)['unit_price'].transform(lambda s: s.fillna(s.median()))

print(df['unit_price'].isna().sum()) # 0

