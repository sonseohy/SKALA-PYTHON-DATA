'''
step 6.
리포트로 예쁘게 출력 + 상위 IP
'''
import csv
from collections import Counter
from functools import reduce

def read_logs(path):
    with open(path, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

def fold(acc, row):
    """누적기(acc)에 row 하나를 반영해서 돌려준다"""
    acc['total'] += 1
    acc['status'][row['status']] += 1
    return acc

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

err_5xx = sum(c for s, c in by_status.items() if str(s).startswith('5'))
ratio = err_5xx / total * 100

print('=' * 40)
print(f'총 요청 수 : {total:,}')
print(f'5xx 오류율 : {ratio:.1f}%')
print('-- 인기 경로 TOP 5 --')
for path, cnt in by_path.most_common(5):
    print(f' {path:<20} {cnt:>7,}')
print('-- 접속 상위 IP TOP 5 --')
for ip, cnt in by_ip.most_common(5):
    print(f' {ip:<20} {cnt:>7,}')
