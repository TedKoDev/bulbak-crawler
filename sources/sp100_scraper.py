import asyncio
import logging
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError
from utils.api import post_stock_data

async def scrape_sp500_stocks():
    """S&P 500 주식들의 상승/하락 데이터를 Finviz에서 수집합니다."""
    gainers = []
    losers = []
    
    logging.info("🔍 S&P 500 데이터 수집 시작...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        
        # 상승/하락 종목 페이지 URL
        gainer_url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500&ft=4&o=-change"  # S&P 500 상승순
        loser_url = "https://finviz.com/screener.ashx?v=111&f=idx_sp500&ft=4&o=change"    # S&P 500 하락순
        
        try:
            page = await context.new_page()
            
            # 상승 종목 수집
            logging.info("📈 상승 종목 수집 중...")
            await page.goto(gainer_url, wait_until="domcontentloaded", timeout=30000)
            
            try:
                # 테이블 로딩 대기
                table_selector = "table.styled-table-new"
                await page.wait_for_selector(table_selector, timeout=30000)
                
                # 상위 20개 종목 추출
                rows = await page.query_selector_all(f"{table_selector} tbody tr")
                for row in rows[:20]:
                    try:
                        cells = await row.query_selector_all("td")
                        
                        symbol = await cells[1].text_content()
                        name = await cells[2].text_content()
                        change_text = await cells[9].text_content()
                        change_percent = float(change_text.strip('%'))
                        
                        stock_data = {
                            "symbol": symbol,
                            "name": name,
                            "change": change_percent,
                            "type": "GAINER",
                            "index": "SP500",
                            "date": datetime.now().isoformat()
                        }
                        
                        if post_stock_data(stock_data):
                            gainers.append(stock_data)
                            logging.info(f"✅ 상승 종목 저장: {symbol} ({change_percent}%)")
                            
                    except Exception as e:
                        logging.error(f"❌ 상승 종목 처리 중 오류: {str(e)}")
            
            except Exception as e:
                logging.error(f"❌ 상승 종목 페이지 처리 중 오류: {str(e)}")
            
            # 하락 종목 수집
            logging.info("📉 하락 종목 수집 중...")
            await page.goto(loser_url, wait_until="domcontentloaded", timeout=30000)
            
            try:
                # 테이블 로딩 대기
                await page.wait_for_selector(table_selector, timeout=30000)
                
                # 상위 20개 종목 추출
                rows = await page.query_selector_all(f"{table_selector} tbody tr")
                for row in rows[:20]:
                    try:
                        cells = await row.query_selector_all("td")
                        
                        symbol = await cells[1].text_content()
                        name = await cells[2].text_content()
                        change_text = await cells[9].text_content()
                        change_percent = float(change_text.strip('%'))
                        
                        stock_data = {
                            "symbol": symbol,
                            "name": name,
                            "change": change_percent,
                            "type": "LOSER",
                            "index": "SP500",
                            "date": datetime.now().isoformat()
                        }
                        
                        if post_stock_data(stock_data):
                            losers.append(stock_data)
                            logging.info(f"✅ 하락 종목 저장: {symbol} ({change_percent}%)")
                            
                    except Exception as e:
                        logging.error(f"❌ 하락 종목 처리 중 오류: {str(e)}")
            
            except Exception as e:
                logging.error(f"❌ 하락 종목 페이지 처리 중 오류: {str(e)}")
            
        except Exception as e:
            logging.error(f"❌ 크롤링 중 오류 발생: {str(e)}")
            
        finally:
            await browser.close()
        
        return gainers + losers

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    results = asyncio.run(scrape_sp500_stocks())
    gainers = [r for r in results if r["type"] == "GAINER"]
    losers = [r for r in results if r["type"] == "LOSER"]
    print(f"🎉 처리 완료: 상승 종목 {len(gainers)}개, 하락 종목 {len(losers)}개") 