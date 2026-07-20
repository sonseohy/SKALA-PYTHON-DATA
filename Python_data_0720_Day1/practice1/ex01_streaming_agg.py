import csv
import tracemalloc
from collections import Counter, defaultdict
from functools import reduce

# CSV 파일 경로 상수로 지정
FILE_PATH = 'web_logs.csv'

# 제너레이터 생성
def read_logs(path):
    with open(path, newline="", encoding='utf-8') as f:
        reader = csv.DictReader(f)  # 첫 줄(헤더)을 키로, 각 행을 값으로 매칭해 CSV 파일의 각 행을 딕셔너리로 변환
        for row in reader:
            yield row


# for 루프로 한 줄씩 읽으며 Counter에 누적
def aggregate_for(path):
    total = 0
    by_status = Counter()
    by_path = Counter()
    by_hour = Counter()
    by_ip = Counter()

    for row in read_logs(path):
        total += 1
        by_status[row['status']] += 1
        by_path[row['path']] += 1
        by_ip[row['ip']] += 1
        hour = row['timestamp'][11:13]  # 'YYYY-MM-DDTHH:MM:SS'에서 시(hour) 부분만 추출
        by_hour[hour] += 1

    return {
        'total': total,
        'status': by_status,
        'path': by_path,
        'hour': by_hour,
        'ip': by_ip,
    }


# 누적기(acc)에 row 하나를 반영하는 함수 (reduce에 넘길 함수)
def fold(acc, row):
    acc['total'] += 1
    acc['status'][row['status']] += 1
    acc['path'][row['path']] += 1
    acc['ip'][row['ip']] += 1
    acc['hour'][row['timestamp'][11:13]] += 1
    return acc


# reduce로 fold를 반복 호출해서 한 번에 누적 집계
def aggregate_reduce(path):
    init = {
        'total': 0,
        'status': Counter(),
        'path': Counter(),
        'hour': Counter(),
        # defaultdict() : 없는 키 접근 시 괄호 안 타입의 기본값을 자동으로 넣어주는 딕셔너리 클래스
        'ip': defaultdict(int),  # 없는 키 접근 시 int의 기본값 0으로 자동 초기화
    }
    return reduce(fold, read_logs(path), init)


# 집계 결과 콘솔에 출력
def print_report(result):
    total = result['total']
    by_status = result['status']
    by_path = result['path']
    by_ip = result['ip']

    err_5xx = sum(c for s, c in by_status.items() if str(s).startswith('5'))
    ratio = err_5xx / total * 100

    print('=' * 40)
    print(f'총 요청 수 : {total:,}')
    print(f'5xx 오류율 : {ratio:.1f}%')
    print('-- 인기 경로 TOP 5 --')
    for path, cnt in by_path.most_common(5):
        print(f' {path:<20} {cnt:>7,}')
    print('-- 접속 상위 IP TOP 5 --')
    # by_ip가 Counter가 아니라 defaultdict일 수도 있으므로 Counter로 감싸서 most_common 사용
    # Counter()로 감싸면 defaultdict를 Counter로 형변환해서 most_common()을 쓸 수 있게 됨
    for ip, cnt in Counter(by_ip).most_common(5):
        print(f' {ip:<20} {cnt:>7,}')

    return total, ratio


# 총 건수와 5xx 비율이 기대값 근처인지 자동으로 확인
def checkpoint(total, ratio):
    print('\n[체크포인트]')
    ok_total = total == 200_000
    ok_ratio = 6.0 <= ratio <= 10.0  # 대략 8% 근방인지 느슨하게 확인

    print(f' - 총 건수 200,000건 여부 : {"PASS" if ok_total else "FAIL"} (실제 {total:,}건)')
    print(f' - 5xx 오류율 ≈8% 여부   : {"PASS" if ok_ratio else "FAIL"} (실제 {ratio:.1f}%)')

    if ok_total and ok_ratio:
        print('체크포인트 통과!')
    else:
        print('체크포인트 기준과 다릅니다. 데이터/로직을 다시 확인하세요.')


# 파일 전체를 통째로 읽어들이는 방식의 최대 메모리 측정
def measure_readlines(path):
    tracemalloc.start()

    with open(path, newline="", encoding='utf-8') as f:
        lines = f.readlines()  # 파일 전체를 한 번에 리스트로 통째로 읽음 (O(n) 메모리)
        reader = csv.DictReader(lines)
        rows = list(reader)  # 딕셔너리 리스트로 전부 메모리에 적재

        total = 0
        by_status = Counter()
        for row in rows:
            total += 1
            by_status[row['status']] += 1

    current, peak = tracemalloc.get_traced_memory()  # (현재 메모리, 최대 메모리) 바이트 단위로 조회
    tracemalloc.stop()
    return peak / 1024 / 1024  # 바이트 -> KB -> MB 순으로 변환


# 제너레이터로 한 줄씩 스트리밍하는 방식의 최대 메모리 측정
def measure_generator(path):
    tracemalloc.start()

    result = aggregate_for(path)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024 / 1024


# 두 방식의 메모리 측정 결과를 나란히 비교 출력
def memory_comparison(path):
    print('\n[확장 과제] tracemalloc 메모리 비교')

    mb_readlines = measure_readlines(path)
    print(f' - readlines() 버전 최대 메모리 : {mb_readlines:.2f} MB')

    mb_generator = measure_generator(path)
    print(f' - 제너레이터 버전 최대 메모리 : {mb_generator:.2f} MB')

    if mb_readlines > 0:
        print(f' - 절감 비율 : 약 {mb_readlines / max(mb_generator, 0.0001):.1f}배 적음')


# 전체 실행: 집계 -> 리포트 -> 검증 -> 체크포인트 -> 메모리 비교
if __name__ == '__main__':
    print('### 1) for 루프 + Counter 온라인 집계 ###')
    result_for = aggregate_for(FILE_PATH)
    total, ratio = print_report(result_for)
    checkpoint(total, ratio)

    print('\n### 2) functools.reduce + fold 패턴 집계 (동일 결과 검증) ###')
    result_reduce = aggregate_reduce(FILE_PATH)
    print_report(result_reduce)

    # for 루프 결과와 reduce 결과가 같은지 교차 검증
    same_total = result_for['total'] == result_reduce['total']
    print(f'\n[검증] for-loop total == reduce total ? {"일치" if same_total else "불일치"}')

    memory_comparison(FILE_PATH)