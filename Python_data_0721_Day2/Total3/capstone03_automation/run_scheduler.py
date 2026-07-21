# run_scheduler.py
import argparse, time
from report import run_once


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=0,
                    help='초 단위 반복. 0이면 1회만 실행')
    ap.add_argument('--mode', choices=['loop', 'schedule'], default='loop',
                    help='반복 방식: loop(기본) 또는 schedule 라이브러리')
    args = ap.parse_args()
    if args.interval == 0:
        run_once(); return
    if args.mode == 'schedule':
        import schedule
        schedule.every(args.interval).seconds.do(run_once)
        while True:
            schedule.run_pending()
            time.sleep(1)  # Ctrl+C 로 중지
    else:
        while True:
            run_once()
            time.sleep(args.interval)  # Ctrl+C 로 중지


if __name__ == '__main__':
    main()
# 실행(루프): python capstone03_automation/run_scheduler.py --interval 60
# 실행(schedule): python capstone03_automation/run_scheduler.py --interval 60 --mode schedule
#
# cron 등록 (crontab -e 로 열어서 추가):
# 0 9 * * * cd /path/skala_python && .venv/bin/python capstone03_automation/report.py >> /path/log.txt 2>&1
# 분 시 일 월 요일 → '0 9 * * *' = 매일 09시 00분
#
# ★ cron 사용 시 3대 주의:
# ① 반드시 '절대 경로' 사용 (cron은 현재 폴더를 모릅니다)
# ② 가상환경 python 을 직접 지정 (.venv/bin/python)
# ③ 로그를 남기세요: >> /path/log.txt 2>&1
