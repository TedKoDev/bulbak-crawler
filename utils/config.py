from dotenv import load_dotenv
import os
import logging

# .env 파일 로드
load_dotenv()

def validate_env_vars():
    required_vars = {
        "REALTIME_URL": "크롤링 대상 URL",
        "CRAWL_INTERVAL_MINUTES": "크롤링 주기(분)"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        error_msg = f"필수 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}"
        logging.error(error_msg)
        raise ValueError(error_msg)

# 환경 변수 검증
try:
    validate_env_vars()
except ValueError as e:
    logging.error(str(e))
    raise

# 환경 변수에서 값 가져오기
# ✅ 여기에 누락된 설정 추가
BASE_API_URL = os.getenv("BASE_API_URL")
REALTIME_URL = os.getenv("REALTIME_URL")
CRAWL_INTERVAL_MINUTES = os.getenv("CRAWL_INTERVAL_MINUTES")