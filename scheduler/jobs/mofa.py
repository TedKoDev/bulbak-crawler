import logging
from datetime import datetime
from sources.mofjab_selenium import run_mofa_job_crawler

def run_mofa_crawler():
    """외교부 채용정보 크롤러 실행"""
    try:
        logging.info("🔄 외교부 채용정보 크롤링 시작")
        run_mofa_job_crawler()
        logging.info("✅ 외교부 채용정보 크롤링 완료")
    except Exception as e:
        logging.error(f"❌ 외교부 채용정보 크롤링 실패: {str(e)}")
        raise 