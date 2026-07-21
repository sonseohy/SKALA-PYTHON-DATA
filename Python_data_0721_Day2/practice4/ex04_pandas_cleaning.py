import pandas as pd

# Pandas 2.x 권장 설정
pd.options.mode.copy_on_write = True

df = pd.read_csv('sales_raw.csv')

# 데이터 크기, 타입, 결측치 현황 확인
print(df.shape)
print(df.dtypes)
print(df.isna().sum())

# 타입 정규화: 문자열을 숫자/날짜/카테고리 타입으로 변환
df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
df['category'] = df['category'].astype('category')
print(df.dtypes)

# 정제 전: 이후 결측/이상치 처리와 비교하기 위해 미리 저장
before_na = df['unit_price'].isna().sum()

# 결측 처리: unit_price 결측치를 카테고리별 중앙값으로 대치
df['unit_price'] = df.groupby('category', observed=True)['unit_price'] \
    .transform(lambda s: s.fillna(s.median()))
after_na = df['unit_price'].isna().sum()

# 이상치 처리 함수: IQR 기준을 벗어난 값을 경계값으로 눌러줌
def winsorize(s, k=1.5):
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - k * iqr, q3 + k * iqr
    return s.clip(lower=low, upper=high)

before_winsor_max = df['unit_price'].max()
df['unit_price'] = winsorize(df['unit_price'])
after_winsor_max = df['unit_price'].max()

# 정제 전후 비교 출력
print(f'결측치 개수      : {before_na} → {after_na}')
print(f'최대값(윈저라이징 전) : {before_winsor_max}')
print(f'최대값(윈저라이징 후) : {after_winsor_max}')

# 매출액 컬럼 계산 후 추가
df['amount'] = df['quantity'] * df['unit_price'] * (1 - df['discount'])

# groupby.agg: 카테고리별 건수/평균가/중앙값/총매출 요약
summary = df.groupby('category', observed=True).agg(
    건수=('unit_price', 'count'),
    평균가=('unit_price', 'mean'),
    중앙값=('unit_price', 'median'),
    총매출=('amount', 'sum'),
).round(1)
print(summary)

# pivot_table: 카테고리 x 지역 매출 교차표
pivot = df.pivot_table(
    index='category',
    columns='region',
    values='amount',
    aggfunc='sum',
    fill_value=0,
)
print(pivot)

# merge용 보조 테이블 생성: 카테고리 활용
other_df = pd.DataFrame({
    'category': ['Beauty', 'Home'],
    'product_type': ['화장품', '가구'],
    'cost_price': [5000, 80000],
    'supplier': ['Supplier_A', 'Supplier_B'],
})

# category 기준으로 왼쪽(df) 전체를 유지하며 merge
merged = df.merge(other_df, on='category', how='left')
print(f'merge 전후 행 수 : {len(df)} → {len(merged)}')
print(merged.head())

# 체인 인덱싱: 중간 결과가 복사본이라 원본이 바뀌지 않음
df[df['unit_price'] > 100]['flag'] = 1
print('체인 인덱싱: ', 'flag' in df.columns)

# .loc 사용: 원본에 직접 접근하므로 정상적으로 반영됨
df.loc[df['unit_price'] > 100, 'flag'] = 1
print('.loc 사용   : ', 'flag' in df.columns)
