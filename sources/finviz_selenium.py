import asyncio
from playwright.async_api import async_playwright
import time
import os
from datetime import datetime

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ✅ 오늘 날짜 기반 파일 이름 생성
TODAY = datetime.now().strftime('%Y-%m-%d')
IMAGE_PATH = f"finviz_map_{TODAY}.png"

# ✅ Google Drive 폴더 ID
FOLDER_ID = "1blggftdSN2IqKwhUN_EhffDFiPTTqSDD"
CREDENTIALS_JSON = "credentials.json"

async def capture_canvas_screenshot():
    try:
        if os.path.exists(IMAGE_PATH):
            os.remove(IMAGE_PATH)
            
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                viewport={'width': 1200, 'height': 800},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
            )
            
            # 우회
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'languages', { get: () => ['ko-KR', 'ko', 'en-US', 'en'] });
                Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            """)
            
            page = await context.new_page()
            await page.goto("https://finviz.com/map.ashx?t=sec", wait_until='domcontentloaded')
            await asyncio.sleep(3)

            # 광고 닫기
            try:
                close_btn = await page.query_selector('#aymStickyFooterClose')
                if close_btn:
                    await close_btn.click()
                    print("✅ 광고 닫기 버튼 클릭 완료")
                    await asyncio.sleep(1)
            except Exception as e:
                print(f"❌ 광고 닫기 클릭 에러: {str(e)}")

            # 광고 제거
            await page.evaluate("""
                const ads = document.querySelectorAll('.adsbygoogle, iframe, [id^="google_ads"], .ad_container');
                ads.forEach(el => el.remove());
                const fixed = document.querySelectorAll('div[style*="position: fixed"], .fixed-bottom');
                fixed.forEach(el => el.remove());
            """)
            print("✅ 광고 및 고정 요소 제거 완료")

            await asyncio.sleep(15)

            canvas = await page.query_selector('canvas.hover-canvas')
            if canvas:
                bbox = await canvas.bounding_box()
                clip = {
                    'x': bbox['x'],
                    'y': bbox['y'],
                    'width': min(bbox['width'], 1200),
                    'height': min(bbox['height'], 800)
                }
                await page.screenshot(path=IMAGE_PATH, clip=clip)
                print(f"✅ 캡처 완료: {IMAGE_PATH}")
            else:
                raise Exception("❌ canvas.hover-canvas 요소를 찾을 수 없습니다.")
            await browser.close()
    except Exception as e:
        print(f"❌ 에러 발생: {str(e)}")
        raise e

def upload_to_drive(filename, folder_id):
    SCOPES = ['https://www.googleapis.com/auth/drive']
    creds = service_account.Credentials.from_service_account_file(CREDENTIALS_JSON, scopes=SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': filename, 'parents': [folder_id]}
    media = MediaFileUpload(filename, mimetype='image/png')
    uploaded_file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ 업로드 완료! File ID: {uploaded_file.get('id')}")

async def main():
    try:
        await capture_canvas_screenshot()
        upload_to_drive(IMAGE_PATH, FOLDER_ID)
    except Exception as e:
        print(f"❌ 프로그램 실행 중 에러 발생: {str(e)}")
    finally:
        if os.path.exists(IMAGE_PATH):
            try:
                os.remove(IMAGE_PATH)
                print("✅ 임시 파일 정리 완료")
            except:
                pass

if __name__ == "__main__":
    asyncio.run(main())
