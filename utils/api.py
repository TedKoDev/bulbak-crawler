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

def get_nasdaq_stocks():
    """
    나스닥 종목 목록을 가져옵니다.
    """
    try:
        res = requests.get(f"{BASE_API_URL}/stocks/nasdaq", timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            logging.warning(f"나스닥 종목 목록 조회 실패 → {res.status_code}")
            return []
    except Exception as e:
        logging.error(f"나스닥 종목 목록 요청 오류: {str(e)}")
        return []

def post_stock_data(stock_data: dict):
    """
    주식 데이터를 API로 전송합니다.
    """
    try:
        res = requests.post(f"{BASE_API_URL}/stocks/us", json=stock_data, timeout=10)
        if res.status_code == 201:
            logging.info(f"[{stock_data['symbol']}] '{stock_data['name']}' 저장 완료")
            return True
        else:
            logging.warning(f"[{stock_data['symbol']}] '{stock_data['name']}' 저장 실패 → {res.status_code}")
            return False
    except Exception as e:
        logging.error(f"[{stock_data['symbol']}] '{stock_data['name']}' 전송 오류: {str(e)}")
        return False

def get_sp500_stocks():
    """
    S&P 500 종목 목록을 가져옵니다.
    """
    try:
        res = requests.get(f"{BASE_API_URL}/stocks/sp500", timeout=10)
        if res.status_code == 200:
            return res.json()
        else:
            logging.warning(f"S&P 500 종목 목록 조회 실패 → {res.status_code}")
            return []
    except Exception as e:
        logging.error(f"S&P 500 종목 목록 요청 오류: {str(e)}")
        return []

def post_stock_mapping(symbol: str, mapping_data: dict, is_sp500: bool = False):
    """
    주식 매핑 데이터를 API로 전송합니다.
    
    Args:
        symbol (str): 미국 주식 심볼
        mapping_data (dict): 매핑 데이터 (krName, krSymbol, reason)
        is_sp500 (bool): S&P 500 종목 여부 (기본값: False)
    """
    try:
        # DTO 형식에 맞게 payload 구성
        payload = {
            "krName": mapping_data["krName"],
            "krSymbol": mapping_data["krSymbol"],
            "reason": mapping_data["reason"],
            "nasdaqSymbol": None if is_sp500 else symbol,
            "sp500Symbol": symbol if is_sp500 else None,
            "marketType": mapping_data["marketType"],
            "correlationType": mapping_data["correlationType"]
        }
        
        res = requests.post(
            f"{BASE_API_URL}/stocks/kr-mappings",
            json=payload,
            timeout=10
        )
        if res.status_code == 201:
            logging.info(f"[{symbol}] → {mapping_data['krName']} 매핑 저장 완료")
            return True
        else:
            logging.warning(f"[{symbol}] → {mapping_data['krName']} 매핑 저장 실패 → {res.status_code}")
            return False
    except Exception as e:
        logging.error(f"[{symbol}] → {mapping_data['krName']} 매핑 전송 오류: {str(e)}")
        return False

