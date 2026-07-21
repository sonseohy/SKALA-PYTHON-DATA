'''
Step 3.
이상치 처리 - IQR 윈저라이징
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# IQR(사분위 범위) 는 데이터를 4등분했을 때 가운데 50%의 폭
# Q1 - 1.5×IQR 보다 작거나, Q3 + 1.5×IQR 보다 크면 이상치

def winsorize(s, k=1.5):
    # 1사분위수(Q1)와 3사분위수(Q3) 계산
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    # 사분범위(IQR) 계산
    iqr = q3 - q1
    # 이상치 범위 정의
    low, high = q1 - k * iqr, q3 + k * iqr
    # clip() : Series의 값들을 지정된 범위 내로 제한하는 메서드
    return s.clip(lower=low, upper=high)    # 삭제가 아니라 끌어당기기 : 이상치를 제거하는 것이 아니라, 범위 밖의 값을 범위의 경계값으로 조정함

print('처리 전 max:', df['unit_price'].max())
df['unit_price'] = winsorize(df['unit_price'])
print('처리 후 max:', df['unit_price'].max())