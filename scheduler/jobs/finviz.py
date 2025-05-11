import logging
import asyncio
from sources.finviz_selenium import main as finviz_main

def run():
    """
    스케줄러에서 실행될 메인 함수
    - Finviz 히트맵 캡처
    - Google Drive 업로드
    """
    logging.info("📡 [FINVIZ] 히트맵 캡처 시작")
    
    try:
        asyncio.run(finviz_main())
        logging.info("✅ [FINVIZ] 히트맵 캡처 및 업로드 완료")
    except Exception as e:
        logging.error(f"❌ [FINVIZ] 작업 실패: {str(e)}") 