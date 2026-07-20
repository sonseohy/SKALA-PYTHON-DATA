'''
step 5.
fold 패턴 — functools.reduce 로 '누적'을 함수로
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

init = {'total': 0, 'status': Counter()}
# reduce()는 초기값부터 시작해서 리스트(또는 반복자)의 각 요소마다 함수를 적용하며 누적해서 최종 하나의 값으로 반환
# reduce(누적함수, 반복자, 초기값) → 초기값부터 시작해서 반복자의 각 요소를 함수로 누적 처리한 최종값 반환
# reduce(함수, 반복자, 초기값)에서 초기값은 누적값으로, 반복자의 요소는 현재요소로 매칭되어 함수(누적값, 현재요소) 형태로 자동 호출
result = reduce(fold, read_logs('../web_logs.csv'), init)
print(result['total'])

# reduce는 for 루프의 누적 패턴을 함수형으로 표현한 것 (초기값부터 시작해서 각 요소를 처리하며 누적)
'''
# for 루프 버전
acc = init
for row in read_logs(...):
    acc = fold(acc, row)

# reduce 버전 (같은 동작)
acc = reduce(fold, read_logs(...), init)
'''