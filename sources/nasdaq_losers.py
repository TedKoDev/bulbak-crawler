import asyncio
import logging
from datetime import datetime
from .base_scraper import BaseFinvizScraper
from utils.api import post_stock_data

class NasdaqLosersScraper(BaseFinvizScraper):
    def __init__(self, max_retries=3, retry_delay=5):
        super().__init__(max_retries, retry_delay)
        self.url = "https://finviz.com/screener.ashx?v=111&s=ta_toplosers&f=exch_nasd&o=change"
    
    async def scrape(self):
        filtered_results = []
        
        p, browser, context = await self._setup_browser()
        
        try:
            page, success = await self._load_page_with_retry(context, self.url)
            if not success:
                logging.error("❌ 최대 재시도 횟수 초과")
                return filtered_results
            
            # Get all rows except header
            rows = await page.query_selector_all("table.styled-table-new tbody tr")
            logging.info(f"📝 총 {len(rows)}개의 행 발견")
            
            current_time = datetime.now()
            
            for row in rows:
                try:
                    # Extract data from each column
                    cells = await row.query_selector_all("td")
                    
                    # Get text content for each cell
                    symbol = await cells[1].text_content()
                    name = await cells[2].text_content()
                    change_percent = float((await cells[9].text_content()).strip('%'))
                    
                    # Format data according to the database schema
                    stock_data = {
                        "symbol": symbol,
                        "name": name,
                        "change": change_percent,  # 이미 음수로 들어옴
                        "type": "LOSER",
                        "index": "NASDAQ100",
                        "date": current_time.isoformat()
                    }
                    
                    if post_stock_data(stock_data):
                        filtered_results.append(stock_data)
                        logging.info(f"✅ {symbol} ({name}) 수집 완료")
                    
                    if len(filtered_results) >= 20:
                        logging.info("🎯 목표 수량(20개) 달성")
                        break
                        
                except Exception as e:
                    logging.error(f"❌ 데이터 추출 중 오류: {str(e)}")
            
        except Exception as e:
            logging.error(f"❌ 크롤링 중 오류 발생: {str(e)}")
        finally:
            await browser.close()
            await p.stop()
            logging.info("🏁 브라우저 종료")
            
        return filtered_results

async def scrape_and_filter_nasdaq_losers():
    scraper = NasdaqLosersScraper()
    return await scraper.scrape()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    results = asyncio.run(scrape_and_filter_nasdaq_losers())
    print(f"🎉 성공적으로 {len(results)}개의 나스닥 하락 종목 처리 완료") 