# jobs/realtime.py
import logging
from sources.realtime_selenium import get_first_source_keywords
from utils.api import post_keywords_to_api

def run():
    """
    스케줄러에서 실행될 메인 함수.
    - 키워드 수집
    - API 전송
    """
    logging.info("📡 [REALTIME] 키워드 수집 시작")

    data = get_first_source_keywords()

    if not data:
        logging.warning("❌ [REALTIME] 키워드 수집 실패 또는 결과 없음")
        return

    post_keywords_to_api(data)
    logging.info("✅ [REALTIME] 키워드 수집 및 저장 완료")
