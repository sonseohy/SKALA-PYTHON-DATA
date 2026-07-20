'''
step 4.
5xx 비율 계산 — 체크포인트 맞추기
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
    hour = row['timestamp'][11:13]
    by_hour[hour] += 1

# 상태코드가 정수일 수 있으니 문자열로 변환해서 '5'로 시작하는지 비교
# .items() = 딕셔너리의 모든 (키, 값) 쌍을 반환하는 메서드
# .startswith() = 문자열이 특정 문자로 시작하는지 확인하는 메서드
err_5xx = sum(c for s, c in by_status.items() if str(s).startswith('5'))
ratio = err_5xx / total * 100
print(f'5xx: {err_5xx}건 ({ratio:.1f}%)')