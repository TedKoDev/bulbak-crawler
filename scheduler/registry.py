# scheduler/registry.py
import schedule
import logging
from datetime import datetime
from scheduler.jobs.realtime import run
from scheduler.jobs.mofa import run_mofa_crawler
from scheduler.jobs.finviz import run as run_finviz
from scheduler.jobs.nasdaq import run as run_nasdaq

def register_jobs():
    """크롤러별 실행 시간 등록 (EC2 UTC 기준)"""
    
    # 실시간 검색어 크롤러 (매 10분마다)
    schedule.every(10).minutes.do(run)
    
    # # 외교부 채용정보 크롤러 (매일 오전 9시, 오후 9시)
    # schedule.every().day.at("09:00").do(run_mofa_crawler)
    # schedule.every().day.at("21:00").do(run_mofa_crawler)
    
    # 외교부 채용정보 크롤러 (한국 시간 오전 6시 = UTC 21:00)
    # schedule.every().day.at("21:00").do(run_mofa_crawler)
    
    # Finviz 히트맵 캡처 (한국 시간 오전 6시 5분 = UTC 21:05)
    schedule.every().day.at("21:05").do(run_finviz)
    
    # Nasdaq 상승 하락 종목 크롤러 (한국 시간 오전 6시 10분 = UTC 21:10)
    schedule.every().day.at("21:10").do(run_nasdaq)

    logging.info("✅ 크롤러 스케줄 등록 완료")
    logging.info(f"📅 등록된 크롤러: 실시간 검색어(10분), 외교부 채용정보(한국시간 06:00), Finviz 히트맵(한국시간 06:05), Nasdaq 종목(한국시간 06:10)")
