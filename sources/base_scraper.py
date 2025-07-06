import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError

class BaseFinvizScraper:
    def __init__(self, max_retries=3, retry_delay=5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
    async def _setup_browser(self):
        p = await async_playwright().start()
        browser = await p.chromium.launch(
            headless=False,
            slow_mo=50,
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        return p, browser, context

    async def _load_page_with_retry(self, context, url):
        page = await context.new_page()
        
        for attempt in range(self.max_retries):
            try:
                logging.info(f"🔄 시도 {attempt + 1}/{self.max_retries}")
                logging.info("🌐 페이지 로딩 시작...")
                
                try:
                    await page.goto(url, timeout=5000)
                except TimeoutError:
                    logging.info("⚠️ 페이지 로딩 시간 초과, 새로고침...")
                    await page.evaluate("window.stop();")
                    await page.reload(timeout=60000)
                    await page.wait_for_timeout(2000)
                
                # Wait for the table to load
                table_selector = "table.styled-table-new"
                await page.wait_for_selector(table_selector, timeout=60000)
                logging.info("✅ 테이블 발견")
                return page, True
                
            except Exception as e:
                logging.error(f"❌ 시도 {attempt + 1} 실패: {str(e)}")
                if attempt < self.max_retries - 1:
                    logging.info(f"⏳ {self.retry_delay}초 후 재시도...")
                    await asyncio.sleep(self.retry_delay)
                    continue
                return page, False 