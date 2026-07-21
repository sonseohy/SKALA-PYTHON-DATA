'''
Step3.
DuckDB 버전 - SQL로 파일 직접 조회
'''

import duckdb, time

start = time.perf_counter()
res_duck = duckdb.sql("""
    SELECT event_type,
        COUNT(*) AS cnt,
        AVG(amount) AS avg
    FROM '../events_large.csv'
    WHERE event_type IN ('purchase', 'refund')
    GROUP BY event_type
    ORDER BY cnt DESC
""").df()

t_duck = (time.perf_counter() - start) * 1000
print(f'DuckDB: {t_duck:.0f} ms')