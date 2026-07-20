import csv
import tracemalloc  # 메모리 사용량을 추적하는 모듈
from collections import Counter
from functools import reduce

def read_logs(path):
    with open(path, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def fold_all(acc, row):
    acc['total'] += 1
    acc['status'][row['status']] += 1
    acc['path'][row['path']] += 1
    acc['hour'][row['timestamp'][11:13]] += 1
    acc['ip'][row['ip']] += 1
    return acc

# ========== 버전 1: for 루프 ==========
print("📊 for 루프 버전 메모리 측정")
tracemalloc.start()  # 메모리 측정 시작

total = 0
by_status = Counter()
by_path = Counter()
by_hour = Counter()
by_ip = Counter()

for row in read_logs('../web_logs.csv'):
    total += 1
    by_status[row['status']] += 1
    by_path[row['path']] += 1
    by_ip[row['ip']] += 1
    hour = row['timestamp'][11:13]
    by_hour[hour] += 1

# 현재 메모리와 최대 메모리 조회 (바이트 단위)
current, peak = tracemalloc.get_traced_memory()  # get_traced_memory(): 메모리 사용량을 조회하는 함수 (현재 메모리, 최대 메모리를 튜플로 반환)
# 바이트를 MB로 변환해서 출력
print(f'최대 메모리: {peak / 1024 / 1024:.2f} MB')  # peak / 1024 / 1024: 바이트를 1024로 두 번 나눠서 MB로 변환 (바이트 → KB → MB)
tracemalloc.stop()  # 메모리 측정 종료

# ========== 버전 2: reduce ==========
print("\n📊 reduce 버전 메모리 측정")
tracemalloc.start()  # 메모리 측정 시작 (새로 시작)

init = {
    'total': 0,
    'status': Counter(),
    'path': Counter(),
    'hour': Counter(),
    'ip': Counter()
}

result = reduce(fold_all, read_logs('../web_logs.csv'), init)

current, peak = tracemalloc.get_traced_memory()
print(f'최대 메모리: {peak / 1024 / 1024:.2f} MB')
tracemalloc.stop()  # 메모리 측정 종료