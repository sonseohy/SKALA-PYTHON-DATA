# run_scheduler.py
import argparse, time
from step7 import run_once
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--interval', type=int, default=0,
                    help='초 단위 반복. 0이면 1회만 실행')
    args = ap.parse_args()
    if args.interval == 0:
        run_once(); return
    while True:
        run_once()
        time.sleep(args.interval) # Ctrl+C 로 중지
# 실행: python capstone03_automation/run_scheduler.py --interval 60
