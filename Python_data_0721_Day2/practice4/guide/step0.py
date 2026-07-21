'''
Step 0.
진단 먼저 - 어디가 얼마나 더러운지 파악
'''

import pandas as pd

df = pd.read_csv('../sales_raw.csv')

print(df.shape)         # 데이터프레임의 행과 열의 개수를 반환
print('=' * 50)
print(df.info())        # 데이터프레임의 각 열의 데이터 타입, null 값 개수, 메모리 사용량 등 전체 정보를 표시
print('=' * 50)
print(df.describe())    # 수치형 데이터의 통계 정보(평균, 최소값, 최대값, 중앙값 등)를 표시
print('=' * 50)
print(df.isna().sum())  # 각 열의 결측치(NaN) 개수
print('=' * 50)
print(df.head())        # 데이터프레임의 처음 몇 행을 보여줌 (기본값: 5행)


# 여기서 확인할 것:
# - price 가 object(문자열)로 잡혀 있진 않은가? → 타입 불일치
#   : unit_price는 float64로 확인됨

# - max 값이 비정상적으로 크지 않은가? → 이상치
#   : quantity max 1995로 확인, 평균 값이 18.56이므로 최대값이 비정상적으로 큰 이상치임을 확인

# - 어느 컬럼에 결측이 몇 개인가? → 결측
#   : region 306개, unit_price 210개 결측