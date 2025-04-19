import schedule
import time
import logging
from main import main
from utils.config import CRAWL_INTERVAL_MINUTES

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)

def job():
    logging.info("스케줄러에 의해 크롤링 작업이 시작됩니다.")
    main()

def run_scheduler():
    if not CRAWL_INTERVAL_MINUTES:
        logging.error("CRAWL_INTERVAL_MINUTES 환경 변수가 설정되지 않았습니다.")
        return

    try:
        interval = int(CRAWL_INTERVAL_MINUTES)
        schedule.every(interval).minutes.do(job)
        
        logging.info(f"스케줄러가 시작되었습니다. {interval}분마다 크롤링을 실행합니다.")
        
        # 초기 실행
        job()
        
        while True:
            schedule.run_pending()
            time.sleep(1)
            
    except ValueError:
        logging.error("CRAWL_INTERVAL_MINUTES는 정수여야 합니다.")
    except Exception as e:
        logging.error(f"스케줄러 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    run_scheduler()
