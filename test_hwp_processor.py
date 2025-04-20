import os
import subprocess
import tempfile
from bs4 import BeautifulSoup

def extract_text_from_hwp_html(hwp_path):
    """HWP 파일을 HTML로 변환하고 텍스트 추출"""
    try:
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            # HWP를 HTML로 변환
            cmd = ["hwp5html", "--output", temp_dir, hwp_path]
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            print(f"Command output: {result.stdout}")
            print(f"Command error: {result.stderr}")
            
            if result.returncode != 0:
                print(f"Error converting HWP to HTML: {result.stderr}")
                return None
                
            # 디렉토리 내용 확인
            print("\nDirectory contents:")
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    print(f"  - {file}")
                    if file.endswith('.xhtml'):
                        html_path = os.path.join(root, file)
                        print(f"Found XHTML file: {html_path}")
                        
                        # XHTML 파일 읽기
                        with open(html_path, 'r', encoding='utf-8') as f:
                            html_content = f.read()
                            print(f"File content length: {len(html_content)} bytes")
                            
                        # HTML에서 텍스트 추출
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text = soup.get_text()
                        return text
                        
            print(f"No XHTML files found in {temp_dir}")
            return None
                
    except Exception as e:
        print(f"Error processing HWP file: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return None

def test_hwp_processing():
    # 다운로드 디렉토리에서 HWP 파일 찾기
    download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "downloads")
    os.makedirs(download_dir, exist_ok=True)
    
    hwp_files = [f for f in os.listdir(download_dir) if f.endswith('.hwp')]
    
    if not hwp_files:
        print(f"Error: No HWP files found in {download_dir}")
        return
        
    # 첫 번째 HWP 파일 사용
    hwp_path = os.path.join(download_dir, hwp_files[0])
    output_path = "output.txt"
    
    print(f"Processing HWP file: {hwp_path}")
    
    # HWP 파일에서 텍스트 추출
    text = extract_text_from_hwp_html(hwp_path)
    if not text:
        print("Failed to extract text from HWP")
        return
        
    # 결과 저장
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print("Successfully processed HWP file!")
        print(f"Extracted text length: {len(text)} characters")
        print(f"Text saved to: {output_path}")
    except Exception as e:
        print(f"Error saving text to {output_path}: {str(e)}")

if __name__ == "__main__":
    test_hwp_processing() 