import pandas as pd
from step0 import CONFIG
from step1 import aggregate
from step3 import render

# 세 가지 방식 모두 결국 같은 함수 하나를 부르게 만드세요
def run_once():
    df = pd.read_csv(CONFIG.data_path)
    data = aggregate(df, CONFIG.top_n)
    path = render(data, CONFIG)
    print(f'리포트 생성: {path}')
# ★ 루프 · schedule · cron 이 전부 run_once() 만 호출
# → 실행 방식이 달라도 결과는 반드시 동일 (일관성)
