'''
step 2.
가장 쉬운 집계 하나만 먼저 (상태코드 개수)
'''
import csv
from collections import Counter

def read_logs(path):
    with open(path, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            yield row

# Counter() : 데이터가 몇 번 나타났는지 자동으로 세는 도구
status_counter = Counter()
total = 0

for row in read_logs('../web_logs.csv'):
    total += 1
    # status_counter는 'status' 열의 값(200, 404, 500 등)을 키로 하고, 각 상태가 나타난 횟수를 값으로 세어줌
    status_counter[row['status']] += 1

print('총 건수:', total)
# most_common()은 가장 많이 나타난 것부터 순서대로 (값, 횟수) 형태로 반환
print(status_counter.most_common(5))