from sources.mofjab_selenium import download_hwp_file

# 테스트할 URL (실제 HWP 파일이 있는 페이지 URL)
TEST_URL = "https://www.mofa.go.kr/www/brd/m_4079/view.do?seq=123456"  # 실제 URL로 변경 필요

def test_download():
    print("Testing HWP file download...")
    hwp_path = download_hwp_file(TEST_URL)
    
    if hwp_path:
        print(f"✅ Successfully downloaded HWP file to: {hwp_path}")
    else:
        print("❌ Failed to download HWP file")

if __name__ == "__main__":
    test_download() 