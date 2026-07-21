'''
Step 0.
오염된 4건이 '어떻게' 오염됐는지 먼저 찾아본다
'''

import json
# json.load() : 열린 파일의 JSON 내용을 Python 객체로 변환
# JSON 파일 로드 후 'results' 키에서 리스트 바로 추출
data = json.load(open('../api_response.json', encoding='utf-8'))['results']

print('전체 건수:', len(data))
# json.dumps() : Python 객체를 JSON 문자열로 변환
print(json.dumps(data[0], indent=2, ensure_ascii=False))    # data[0]: 객체, indent=2: 들여쓰기, ensure_ascii=False: 한글 그대로

# 어떤 키들이 있는지, 값 타입이 뭔지 확인 (data 전체 확인)
for i, row in enumerate(data):
    # 딕셔너리 컴프리헨션 : row.items()로 (키,값) 가져와 k는 원래 키 그대로 사용, type(v)로 값의 타입을 구하고 __name__으로 해당 타입을 문자열로 변환
    # __name__ : 데이터 타입의 이름을 문자열로 반환 (예: int.__name__ = 'int')
    print(i, {k: type(v).__name__ for k, v in row.items()})

# 힌트: 음수 가격 / 타입 이상 / 필수 필드 누락 / 범위 초과 를 의심하세요
# 데이터 직접 확인
# id=7  : age가 음수(-5) (범위 위반)
# id=13 : email이 "not-an-email" (형식 위반)
# id=21 : email 필드 자체가 없음 (필수 필드 누락)
# id=29 : profile.score가 150.0 (범위 초과)