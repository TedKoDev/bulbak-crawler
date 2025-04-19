from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException
from bs4 import BeautifulSoup
import time
import logging
from utils.config import FIRST_URL

PLATFORMS = ["daum", "zum", "nate", "googletrend"]

def get_adsensefarm_keywords():
    if not FIRST_URL:
        logging.error("FIRST_URL이 설정되지 않았습니다.")
        return {}

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(30)
        driver.get(FIRST_URL)

        time.sleep(3)  # JS 로딩 대기

        soup = BeautifulSoup(driver.page_source, "html.parser")
        result = {}

        for platform in PLATFORMS:
            try:
                section = soup.find("div", {"class": "item", "id": platform})
                if not section:
                    logging.warning(f"{platform} 섹션을 찾을 수 없습니다.")
                    continue

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
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    from datetime import datetime
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] Selenium 기반 키워드 수집 결과:")

    data = get_adsensefarm_keywords()
    for platform, keywords in data.items():
        print(f"\n[{platform.upper()}]")
        for i, keyword in enumerate(keywords, 1):
            print(f"{i}. {keyword}")
