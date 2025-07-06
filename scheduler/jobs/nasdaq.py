import logging
import asyncio
from sources.nasdaq_gainers import scrape_and_filter_nasdaq_gainers
from sources.nasdaq_losers import scrape_and_filter_nasdaq_losers

def run():
    """
    스케줄러에서 실행될 메인 함수
    - Nasdaq 상승 종목 크롤링
    - Nasdaq 하락 종목 크롤링
    """
    logging.info("📡 [NASDAQ] 상승 종목 크롤링 시작")
    
    try:
        asyncio.run(scrape_and_filter_nasdaq_gainers())
        logging.info("✅ [NASDAQ] 상승 종목 크롤링 완료")
        logging.info("📡 [NASDAQ] 하락 종목 크롤링 시작")
        asyncio.run(scrape_and_filter_nasdaq_losers())
        logging.info("✅ [NASDAQ] 하락 종목 크롤링 완료")
    except Exception as e:
        logging.error(f"❌ [NASDAQ] 작업 실패: {str(e)}") 