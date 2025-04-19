# scheduler/runner.py
import time
import logging
import schedule
from scheduler.registry import register_jobs  # 절대 경로만 사용

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def run_scheduler():
    register_jobs()
    logging.info("⏱️ 스케줄러 시작!")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler()