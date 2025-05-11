# scheduler/registry.py
import schedule
import logging
from datetime import datetime
from scheduler.jobs.realtime import run
from scheduler.jobs.mofa import run_mofa_crawler
from scheduler.jobs.finviz import run as run_finviz

def register_jobs():
    """크롤러별 실행 시간 등록"""
    
    # 실시간 검색어 크롤러 (매 10분마다)
    schedule.every(1).minutes.do(run)
    
    # 외교부 채용정보 크롤러 (매일 오전 9시, 오후 9시)
    schedule.every().day.at("09:00").do(run_mofa_crawler)
    schedule.every().day.at("21:00").do(run_mofa_crawler)
    
    # Finviz 히트맵 캡처 (매일 장 마감 후 오전 6시)
    schedule.every().day.at("06:15").do(run_finviz)
    
    logging.info("✅ 크롤러 스케줄 등록 완료")
    logging.info(f"📅 등록된 크롤러: 실시간 검색어(1분), 외교부 채용정보(매일 09:00, 21:00), Finviz 히트맵(매일 06:15)")
