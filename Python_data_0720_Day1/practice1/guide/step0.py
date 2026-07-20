'''
step 0.
앞 5줄만 출력해서 컬럼 이름과 형태를 확인
'''
# 파일을 열고, with 블록이 끝나면 자동으로 닫기
with open('../web_logs.csv') as f:
    # enumerate : 파일에서 한 줄씩 읽어 (인덱스, 한 줄 내용) 튜플로 반환 → 사용 후 그 줄은 버리고 다음 줄 읽음 (메모리 효율적)
    for i, line in enumerate(f):    
        # .strip() : 앞뒤 공백/개행문자 제거
        print(line.strip())
        if i >= 4:
            break

