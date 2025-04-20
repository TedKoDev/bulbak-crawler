import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, parse_qs, urlparse
from datetime import datetime
import os
import tempfile
import subprocess
import re
import shutil
from utils.api import post_crawled_data_to_api  # ✅ 크롤링 결과 백엔드로 전송
from utils.config import MOFA_URL
from pdf2image import convert_from_path
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
from PIL import Image
import io


LIST_URL = f"{MOFA_URL}/www/brd/m_4079/list.do"
DETAIL_URL_BASE = f"{MOFA_URL}/www/brd/m_4079/view.do"

# 작업 디렉토리 설정
WORKSPACE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONVERSION_DIR = os.path.join(WORKSPACE_DIR, "conversion_temp")
os.makedirs(CONVERSION_DIR, exist_ok=True)

def convert_hwp_to_images(hwp_path, output_dir=None):
    """Convert HWP file to images using LibreOffice"""
    try:
        # 출력 디렉토리 설정
        if output_dir is None:
            output_dir = CONVERSION_DIR
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Convert HWP to PDF first
        base_name = os.path.splitext(os.path.basename(hwp_path))[0]
        temp_pdf = os.path.join(output_dir, f"{base_name}.pdf")
        
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            "--outdir", output_dir,
            hwp_path
        ]
        
        print(f"Converting HWP to PDF: {' '.join(cmd)}")
        print(f"Input HWP path: {hwp_path}")
        print(f"Output directory: {output_dir}")
        print(f"Target PDF path: {temp_pdf}")
        
        # Check if input file exists
        if not os.path.exists(hwp_path):
            print(f"Error: Input HWP file does not exist at {hwp_path}")
            return None
            
        # Check file permissions
        if not os.access(hwp_path, os.R_OK):
            print(f"Error: No read permission for HWP file at {hwp_path}")
            return None
            
        # Check output directory permissions
        if not os.access(output_dir, os.W_OK):
            print(f"Error: No write permission for output directory {output_dir}")
            return None
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        print(f"Command stdout: {result.stdout}")
        print(f"Command stderr: {result.stderr}")
        
        if result.returncode != 0:
            print(f"Error converting HWP to PDF: {result.stderr}")
            return None
            
        # Check if PDF was created
        if not os.path.exists(temp_pdf):
            print(f"Error: PDF file was not created at {temp_pdf}")
            print("Directory contents:")
            for f in os.listdir(output_dir):
                print(f"  - {f}")
            return None
            
        # Convert PDF to images
        print(f"Converting PDF to images from {temp_pdf}")
        try:
            images = convert_from_path(temp_pdf)
        except Exception as e:
            print(f"Error converting PDF to images: {str(e)}")
            return None
            
        # Save images
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.png")
            image.save(image_path, "PNG")
            image_paths.append(image_path)
            print(f"Saved image: {image_path}")
            
        # Clean up temporary PDF
        try:
            os.remove(temp_pdf)
            print(f"Removed temporary PDF: {temp_pdf}")
        except Exception as e:
            print(f"Warning: Failed to remove temporary PDF: {str(e)}")
            
        return image_paths
        
    except Exception as e:
        print(f"Error in convert_hwp_to_images: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def extract_text_from_images(image_paths):
    """Extract text from images using Tesseract OCR"""
    try:
        full_text = ""
        for image_path in image_paths:
            print(f"Processing image: {image_path}")
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='kor+eng')
            full_text += text + "\n"
        return full_text
    except Exception as e:
        print(f"Error in extract_text_from_images: {str(e)}")
        return None

def clean_extracted_text(text):
    """Clean the extracted text"""
    if not text:
        return ""
        
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove special characters
    text = text.replace('\x0c', '')  # Form feed character
    
    return text

def format_table(table_data):
    """표 데이터 포맷팅"""
    if not table_data:
        return []
        
    # 각 열의 최대 너비 계산
    col_widths = []
    for row in table_data:
        while len(col_widths) < len(row):
            col_widths.append(0)
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))
    
    # 표 형식으로 포맷팅
    formatted_table = []
    border = '+' + '+'.join('-' * (w + 2) for w in col_widths) + '+'
    formatted_table.append(border)
    
    for row in table_data:
        cells = []
        for i, cell in enumerate(row):
            if i < len(col_widths):
                cells.append(f' {cell:<{col_widths[i]}} ')
        formatted_table.append('|' + '|'.join(cells) + '|')
        formatted_table.append(border)
    
    return formatted_table

def clean_content(content):
    """추출된 내용 정리"""
    if not content:
        return ""
        
    # 줄 단위로 처리
    lines = []
    prev_line = ""
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            if prev_line:  # 연속된 빈 줄 제거
                lines.append("")
                prev_line = ""
            continue
            
        # 표 형식 유지
        if line.startswith('+') and line.endswith('+'):
            lines.append(line)
            prev_line = line
            continue
            
        # 일반 텍스트 처리
        if line != prev_line:  # 중복 라인 제거
            lines.append(line)
            prev_line = line
    
    # 마지막 빈 줄 제거
    while lines and not lines[-1]:
        lines.pop()
        
    return '\n'.join(lines)

def parse_job_list_page(page=1):
    url = f"{LIST_URL}?page={page}"
    print(f"Fetching URL: {url}")  # URL 출력
    
    response = requests.get(url)
    print(f"Response status: {response.status_code}")  # 응답 상태 출력
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 디버깅: HTML 구조 출력
    print("Page structure:")
    print(soup.prettify()[:500])  # 처음 500자만 출력
    
    rows = soup.select("table.tableB tbody tr")
    print(f"Found {len(rows)} rows")  # 발견된 행 수 출력
    
    job_data = []
    target_date = datetime.now().date()  # 당일 날짜 사용

    for idx, row in enumerate(rows):
        try:
            cols = row.select("td")
            print(f"\nProcessing row {idx + 1}, columns: {len(cols)}")  # 행 처리 정보 출력
            
            if len(cols) < 6:
                print(f"Skipping row {idx + 1}: insufficient columns")
                continue

            title_el = cols[2].find("a")
            if not title_el:
                print(f"Skipping row {idx + 1}: no title link found")
                continue
                
            title = title_el.get_text(strip=True)
            href = title_el.get("href", "")
            if not href:
                print(f"Skipping row {idx + 1}: no href found")
                continue
                
            full_url = urljoin(LIST_URL, href)
            date_str = cols[5].text.strip()
            
            print(f"Row {idx + 1} data:")
            print(f"  Title: {title}")
            print(f"  Date: {date_str}")
            
            if not date_str or len(date_str) != 10:
                print(f"Skipping row {idx + 1}: invalid date format")
                continue
                
            write_date = datetime.strptime(date_str, "%Y-%m-%d")

            # 월과 일만 비교
            if write_date.month == target_date.month and write_date.day == target_date.day:
                print(f"Found matching posting: {title} - {date_str}")
                job_data.append({
                    "title": title,
                    "link": full_url,
                    "write_date": date_str,
                    "department": cols[4].text.strip(),
                })
        except Exception as e:
            print(f"Error processing row {idx + 1}: {str(e)}")
            continue

    print(f"\nFound {len(job_data)} matching jobs")
    return job_data

def download_hwp_file(url):
    """HWP 파일 다운로드"""
    try:
        # 상세 페이지에서 다운로드 링크 찾기
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        
        try:
            print(f"Accessing URL: {url}")
            driver.get(url)
            wait = WebDriverWait(driver, 10)
            
            # 파일 링크 찾기
            file_link = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='down.do']"))
            )
            download_url = file_link.get_attribute('href')
            
            if not download_url:
                print("Download URL not found")
                return None
                
            # 상대 경로를 절대 경로로 변환
            if download_url.startswith('./'):
                base_url = '/'.join(url.split('/')[:-1])
                download_url = f"{base_url}/{download_url[2:]}"
            elif download_url.startswith('/'):
                base_url = '/'.join(url.split('/')[:3])
                download_url = f"{base_url}{download_url}"
                
            print(f"Found download URL: {download_url}")
            
            # 파일명 추출
            file_name = file_link.text.strip()
            if not file_name:
                file_name = "downloaded.hwp"
            
            # 다운로드 디렉토리 생성
            download_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "downloads")
            os.makedirs(download_dir, exist_ok=True)
            
            # 파일 경로 설정
            file_path = os.path.join(download_dir, file_name)
            
            # 파일 다운로드
            response = requests.get(download_url, allow_redirects=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded HWP file to: {file_path}")
                print(f"File size: {len(response.content)} bytes")
                return file_path
            else:
                print(f"Failed to download file. Status code: {response.status_code}")
                return None
                
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error downloading HWP file: {str(e)}")
        return None

def extract_text_from_hwp_html(hwp_path):
    """HWP 파일을 HTML로 변환하고 텍스트 추출"""
    try:
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # HWP를 HTML로 변환
            cmd = ["hwp5html", "--output", temp_dir, hwp_path]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error converting HWP to HTML: {result.stderr}")
                return None
                
            # HTML 파일 읽기
            html_path = os.path.join(temp_dir, "index.xhtml")
            if os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                # HTML에서 텍스트 추출
                soup = BeautifulSoup(html_content, 'html.parser')
                text = soup.get_text()
                return text
            else:
                print(f"HTML file not found at {html_path}")
                return None
                
    except Exception as e:
        print(f"Error processing HWP file: {str(e)}")
        return None

def get_content_from_hwp(url):
    """HWP 파일 다운로드 및 텍스트 추출"""
    try:
        # HWP 파일 다운로드
        hwp_path = download_hwp_file(url)
        if not hwp_path:
            print("Failed to download HWP file")
            return None
            
        try:
            # HWP에서 텍스트 추출
            text = extract_text_from_hwp_html(hwp_path)
            if text:
                return clean_content(text)
            else:
                print("Failed to extract text from HWP")
                return None
                
        except Exception as e:
            print(f"Error processing HWP file: {str(e)}")
            return None
                
    except Exception as e:
        print(f"Error processing HWP file: {str(e)}")
        return None

def parse_job_detail(url):
    """채용공고 상세 페이지 파싱"""
    try:
        # HWP 파일에서 내용 추출 시도
        content = get_content_from_hwp(url)
        if content:
            return content
            
        # 실패시 페이지 내용 직접 추출 시도
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(url)
            content_el = driver.find_element(By.CSS_SELECTOR, ".bo_con")
            if content_el:
                return clean_content(content_el.text)
                
            return "내용을 찾을 수 없습니다."
            
        finally:
            driver.quit()
            
    except Exception as e:
        print(f"Error parsing job detail: {str(e)}")
        return "내용을 가져오는데 실패했습니다."

def run_mofa_job_crawler():
    results = []
    
    # 여러 페이지 확인
    for page in range(1, 4):  # 1~3페이지까지 확인
        items = parse_job_list_page(page=page)
        
        for item in items:
            content = parse_job_detail(item["link"])

            results.append({
                "site": "MOFA 채용정보",
                "url": item["link"],
                "type": "JOB",
                "title": item["title"],
                "content": content,
            })

    # 중복 제거
    unique_results = []
    seen = set()
    for result in results:
        if result["url"] not in seen:
            unique_results.append(result)
            seen.add(result["url"])

    if unique_results:
        post_crawled_data_to_api(unique_results)
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"✅ 총 {len(unique_results)}건 발견 ({today} 공고)")
    else:
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"📭 {today} 채용 공고가 없습니다.")

if __name__ == "__main__":
    run_mofa_job_crawler()
