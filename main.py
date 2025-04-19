import logging
from sources.adfirst_selenium import get_adsensefarm_keywords
from utils.config import FIRST_URL

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('crawler.log'),
        logging.StreamHandler()
    ]
)

def main():
    if not FIRST_URL:
        logging.error("FIRST_URL 환경 변수가 설정되지 않았습니다.")
        return

    try:
        logging.info("크롤링을 시작합니다...")
        data = get_adsensefarm_keywords()
        
        for platform, keywords in data.items():
            logging.info(f"[{platform.upper()}] {len(keywords)}개의 키워드를 수집했습니다.")
            
        logging.info("크롤링이 완료되었습니다.")
        return data
        
    except Exception as e:
        logging.error(f"크롤링 중 오류 발생: {str(e)}")
        return None

if __name__ == "__main__":
    main()
