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
                res = requests.post(f"{BASE_API_URL}/search-terms", json=payload, timeout=10)
                if res.status_code == 201:
                    logging.info(f"[{platform}] {rank}. '{keyword}' 저장 완료")
                else:
                    logging.warning(f"[{platform}] {rank}. '{keyword}' 저장 실패 → {res.status_code}")
            except Exception as e:
                logging.error(f"[{platform}] '{keyword}' 전송 오류: {str(e)}")

def post_crawled_data_to_api(results: list):
    for payload in results:
        try:
            # 필수 필드만 포함하여 check 요청
            check_payload = {"url": payload["url"]}
            check_res = requests.get(
                f"{BASE_API_URL}/crawl-data/check",
                json=check_payload,
                timeout=10
            )
            
            if check_res.status_code == 200:
                check_data = check_res.json()
                if check_data.get("exists"):
                    # 이미 존재하면 title과 content만 업데이트
                    update_payload = {
                        "url": payload["url"],
                        "title": payload["title"],
                        "content": payload["content"]
                    }
                    res = requests.put(
                        f"{BASE_API_URL}/crawl-data",
                        json=update_payload,
                        timeout=10
                    )
                    if res.status_code == 200:
                        logging.info(f"[{payload['site']}] '{payload['title']}' 업데이트 완료")
                    else:
                        logging.warning(f"[{payload['site']}] '{payload['title']}' 업데이트 실패 → {res.status_code}")
                    continue
            
            # 없는 경우 새로 생성
            create_payload = {
                "site": payload["site"],
                "url": payload["url"],
                "type": payload["type"],
                "title": payload.get("title"),  # optional
                "content": payload.get("content")  # optional
            }
            res = requests.post(
                f"{BASE_API_URL}/crawl-data",
                json=create_payload,
                timeout=10
            )
            if res.status_code == 201:
                logging.info(f"[{payload['site']}] '{payload['title']}' 저장 완료")
            else:
                logging.warning(f"[{payload['site']}] '{payload['title']}' 저장 실패 → {res.status_code}")
        except Exception as e:
            logging.error(f"[{payload['site']}] '{payload['title']}' 전송 오류: {str(e)}")

def get_s3_presigned_url(key: str, content_type: str = 'image/png') -> dict:
    """
    S3 presigned URL을 백엔드로부터 받아옵니다.
    """
    try:
        payload = {
            "key": key,
            "type": "put",
            "contentType": content_type
        }
        res = requests.post(
            f"{BASE_API_URL}/s3/presigned-url",
            json=payload,
            timeout=10
        )
        
        if res.status_code == 201 or res.status_code == 200:
            return res.json()
        else:
            logging.warning(f"Presigned URL 생성 실패 → {res.status_code}")
            raise Exception(f"Failed to get presigned URL: {res.status_code}")
    except Exception as e:
        logging.error(f"Presigned URL 요청 오류: {str(e)}")
        raise e

