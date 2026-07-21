'''
Step 7.
Copy-on-Write 이해하기 (Pandas 2.x의 새 규칙)
'''
import pandas as pd

df = pd.read_csv('../sales_raw.csv')

# 예전 Pandas에서 `SettingWithCopyWarning`이라는 수정했는데 원본이 바뀌지 않은 문제가 많이 발생함
# Copy-on-Write(CoW) 는 이걸 정리한 새 규칙: "슬라이스는 항상 복사본처럼 동작한다. 원본을 바꾸려면 원본에 직접 써라. → 불필요한 복사가 줄어 성능도 좋아짐

pd.options.mode.copy_on_write = True    # Pandas 2.x 권장 설정

# 체인 인덱싱 - 원본이 변경 X
df[df['unit_price'] > 100]['flag'] = 1
print("체인 인덱싱: ", 'flag' in df.columns)

# .loc 사용 - 원본이 변경
df.loc[df['unit_price'] > 100, 'flag'] = 1
print(".loc 사용: ", 'flag' in df.columns)