'''
Step 1.
기준선 만들기 - Pandas 버전 (가장 익숙한 것부터)
'''

import pandas as pd, time

start = time.perf_counter()
df = pd.read_csv('../events_large.csv')


# purchase 또는 refund인 데이터만 필터링 → event_type별로 그룹화 → 개수/평균 계산
res_pandas = (
    df[(df['event_type'] == 'purchase') | (df['event_type'] == 'refund')]
    .groupby('event_type')
    .agg(
        cnt=('amount', 'count'),
        avg=('amount', 'mean')
    )
    .sort_values('cnt', ascending=False)    # cnt 기준 내림차순 정렬
    .reset_index()
)

# time.perf_counter(): 고정도 타이머 (나노초 단위)
# 실행 시간을 밀리초 단위로 계산
t_pandas = (time.perf_counter() - start) * 1000 # (끝 - 시작) * 1000: 밀리초 단위로 변환
print(f'Pandas: {t_pandas:.0f} ms') # ≈ 1,668 ms
print(res_pandas.head())