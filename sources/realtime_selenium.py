# Selenium 및 BeautifulSoup 기반 실시간 키워드 수집기

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
import time
import logging
from utils.config import REALTIME_URL              # .env에서 설정한 수집 대상 URL
from utils.api import post_keywords_to_api      # 수집된 데이터를 백엔드 API로 전송

# 수집 대상 플랫폼 ID들 (HTML의 id 속성 기준)
PLATFORMS = ["daum", "zum", "nate", "googletrend"]

def get_first_source_keywords():
    """
    Selenium으로 지정된 URL에서 각 플랫폼별 실시간 키워드를 수집한다.
    수집 실패 시 로깅하고 빈 딕셔너리 반환.
    """
    if not REALTIME_URL:
        logging.error("REALTIME_URL이 설정되지 않았습니다.")
        return {}

    # 브라우저 옵션 설정 (봇 감지 회피)
    options = Options()
    options.add_argument("--headless")  # 창 없이 실행
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    
    # 봇 감지 회피를 위한 추가 옵션
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-infobars")
    
    # 실제 브라우저처럼 보이도록 User-Agent 설정
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36")

    driver = None
    try:
        # Chrome WebDriver 실행
        driver = webdriver.Chrome(options=options)
        
        # 봇 감지 회피를 위한 추가 설정
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        })
        
        driver.set_page_load_timeout(30)
        driver.get(REALTIME_URL)

        time.sleep(5)  # JavaScript가 키워드를 렌더링할 시간 확보

        # 페이지 전체를 BeautifulSoup으로 파싱
        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = {}

        for platform in PLATFORMS:
            try:
                # 각 플랫폼의 검색어 박스를 찾음
                section = soup.find("div", {"class": "item", "id": platform})
                if not section:
                    logging.warning(f"{platform} 섹션을 찾을 수 없습니다.")
                    continue

                # 각 키워드 텍스트 추출
                keywords = [a.text.strip() for a in section.select("span.keyword > a")]
                if not keywords:
                    logging.warning(f"{platform}에서 키워드를 찾을 수 없습니다.")
                    continue

                result[platform] = keywords
                logging.info(f"{platform}에서 {len(keywords)}개의 키워드를 수집했습니다.")

            except Exception as e:
                logging.error(f"{platform} 처리 중 오류 발생: {str(e)}")
                continue

        return result

    except WebDriverException as e:
        logging.error(f"웹드라이버 오류 발생: {str(e)}")
        return {}
    except TimeoutException:
        logging.error("페이지 로딩 시간 초과")
        return {}
    except Exception as e:
        logging.error(f"예상치 못한 오류 발생: {str(e)}")
        return {}
    finally:
        # 브라우저 종료
        if driver:
            try:
                driver.quit()
            except:
                pass

# 🔍 수집 결과 콘솔 출력
if __name__ == "__main__":
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Selenium 기반 키워드 수집 결과:")

    data = get_first_source_keywords()
    for platform, keywords in data.items():
        print(f"\n[{platform.upper()}]")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")

    # 💾 수집 결과 백엔드 API로 전송
    post_keywords_to_api(data)
