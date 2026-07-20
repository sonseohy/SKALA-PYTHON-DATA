'''
step 3.
지표를 늘린다 — 경로별 · 시간대별 · IP별
'''
import csv
from collections import Counter, defaultdict

def read_logs(path):
    with open(path, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

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
    # row['timestamp'][11:13]는 타임스탬프 문자열에서 11번째부터 13번째 직전까지 자른 것 (시간 추출) 
    hour = row['timestamp'][11:13]
    by_hour[hour] += 1