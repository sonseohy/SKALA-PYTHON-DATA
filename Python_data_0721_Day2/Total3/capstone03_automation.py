import argparse
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader


@dataclass(frozen=True)
class Config:
    data_path: Path = Path('data/sales_raw.csv')
    output_dir: Path = Path('output')
    template_dir: Path = Path('templates')
    top_n: int = 10
    title: str = '매출 리포트'


CONFIG = Config()


def aggregate(df: pd.DataFrame, top_n: int = 10) -> dict:
    """데이터 → 리포트에 넣을 값들. 파일은 안 건드림(순수 함수)"""
    return {
        'kpi': {
            '총매출': int(df['amount'].sum()),
            '주문수': len(df),
            '평균주문액': round(df['amount'].mean(), 1),
        },
        'by_category': (df.groupby('category', observed=True)['amount']
                         .sum().sort_values(ascending=False)
                         .head(top_n).reset_index()
                         .to_dict('records')),
    }


def render(data: dict, cfg) -> Path:
    env = Environment(loader=FileSystemLoader(str(cfg.template_dir)))
    tpl = env.get_template('report.html')
    html = tpl.render(
        title=cfg.title,
        generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        **data,
    )
    cfg.output_dir.mkdir(parents=True, exist_ok=True)
    # ★ 타임스탬프를 파일명에 → 이전 리포트가 안 지워짐
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    out = cfg.output_dir / f'report_{stamp}.html'
    out.write_text(html, encoding='utf-8')
    return out


# 세 가지 방식 모두 결국 같은 함수 하나를 부르게 만드세요
def run_once():
    df = pd.read_csv(CONFIG.data_path)
    data = aggregate(df, CONFIG.top_n)
    path = render(data, CONFIG)
    print(f'리포트 생성: {path}')
    return path
# ★ 루프 · schedule · cron 이 전부 run_once() 만 호출
# → 실행 방식이 달라도 결과는 반드시 동일 (일관성)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=0,
                    help='초 단위 반복. 0이면 1회만 실행')
    args = ap.parse_args()
    if args.interval == 0:
        run_once(); return
    while True:
        run_once()
        time.sleep(args.interval)  # Ctrl+C 로 중지
# 실행: python capstone03_automation.py --interval 60


if __name__ == '__main__':
    main()
