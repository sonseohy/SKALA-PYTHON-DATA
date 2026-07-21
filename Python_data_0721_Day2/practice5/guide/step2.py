'''
Step 2.
Polars Lazy 버전 - scan_csv + collect
'''

import polars as pl, time

start = time.perf_counter()

# purchase 또는 refund인 데이터만 필터링 → event_type별로 그룹화 → 개수/평균 계산
res_polars = (
    # 'scan'은 읽겠다고 계획만 세움, 실제 실행은 .collect()에서 일어남 (read_csv X)
    pl.scan_csv('../events_large.csv')  # ★ scan (지연 실행)
    .filter(pl.col('event_type').is_in(['purchase', 'refund']))
    .group_by('event_type')
    .agg([
        pl.len().alias('cnt'),  #.alias() : 결과에 새 이름을 부여하는 메서드
        pl.col('amount').mean().alias('avg')
    ])
    .sort('cnt', descending=True)
    .collect()  # ★ 여기서 실제 실행
    #.explain()
)

# 실행 시간을 밀리초 단위로 계산
t_polars = (time.perf_counter() - start) * 1000
print(f'Polars: {t_polars:.0f} ms')
print(res_polars)