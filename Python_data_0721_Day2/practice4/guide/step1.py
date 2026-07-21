'''
Step 1.
타입 정규화 - 숫자는 숫자로, 날짜는 날짜로
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# 문자열 → 숫자 (실패한 값은 NaN으로)
# pd.to_numeric() : 텍스트를 숫자로 변환하는 함수
df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce')   # errors='coerce'(권장) : 변환 실패 시 → NaN으로 변환
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

# 문자열 → 날짜
df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

# 범주형은 category 타입으로 (메모리 절약 + 속도)
df['category'] = df['category'].astype('category')

print(df.dtypes)    # order_date → (str에서) datetime으로 변경, category → (str에서) category 타입 변경 확인

'''
errors 파라미터 옵션
- errors='raise' (기본값) : 변환 실패 시 → 에러 발생
- errors='ignore' : 변환 실패 시 → 원본 값 유지
'''

# 순서 주의! 타입 변환을 먼저 하면, 변환 실패한 값이 NaN이 되면서 결측 개수가 늘어납니다. 그래서 결측처리는 반드시 타입 정규화 다음에 합니다.