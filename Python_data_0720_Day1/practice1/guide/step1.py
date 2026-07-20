'''
step 1.
한 줄을 '딕셔너리 하나'로 바꾸는 제너레이터 만들기
'''
# csv 파일 읽고 쓰기 위한 Python 내장 모듈
import csv

def read_logs(path):
    # newline은 Python이 \n, \r\n, \r 등 모든 줄바꿈을 자동으로 처리하도록 함
    # encoding은 파일의 문자 인코딩 방식 설정. UTF-8은 한글 지원하는 인코딩
    with open(path, newline="", encoding='utf-8') as f:
        # csv.DictReader() : CSV 파일의 각 행을 딕셔너리로 변환
        #                  : 첫 줄(열이름)을 키로, 각 행의 값을 해당 키의 값으로 자동 매칭
        reader = csv.DictReader(f)
        for row in reader:
            # yield는 값을 반환하고 함수를 일시 중지했다가, 다시 호출되면 중지된 위치부터 계속 실행
            yield row

gen = read_logs('../web_logs.csv')
for _ in range(3):
    # next()는 반복자(iterator)에서 다음 값을 하나씩 꺼내는 파이썬 내장 함수
    print(next(gen))