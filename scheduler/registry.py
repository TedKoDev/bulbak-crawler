# scheduler/registry.py
import schedule
from scheduler.jobs import realtime
from utils.config import CRAWL_INTERVAL_MINUTES

def register_jobs():
    interval = int(CRAWL_INTERVAL_MINUTES)  # 환경 변수에서 가져온 간격 사용
    schedule.every(interval).minutes.do(realtime.run)
