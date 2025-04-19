# utils/api.py
import requests
import logging
from datetime import datetime
from utils.config import BASE_API_URL

def post_keywords_to_api(result: dict):
    now = datetime.now().isoformat()

    for platform, keywords in result.items():
        for rank, keyword in enumerate(keywords, start=1):
            payload = {
                "platform": platform,
                "keyword": keyword,
                "rank": rank,
                "collectedAt": now
            }
            try:
                res = requests.post(f"{BASE_API_URL}/search-term", json=payload, timeout=10)
                if res.status_code == 201:
                    logging.info(f"[{platform}] {rank}. '{keyword}' 저장 완료")
                else:
                    logging.warning(f"[{platform}] {rank}. '{keyword}' 저장 실패 → {res.status_code}")
            except Exception as e:
                logging.error(f"[{platform}] '{keyword}' 전송 오류: {str(e)}")
