# Bulbak Crawler

🚀 **Bulbak** 프로젝트의 크롤링 전용 서브 시스템

---

## 📌 개요

이 저장소는 Bulbak 자동화 블로그 시스템을 위한 **데이터 수집기(Crawler)** 를 구성합니다.  
Zoom, Naver, Daum, Nate, Google Trends 등 다양한 포털에서 실시간 검색어를 주기적으로 수집하여 메인 백엔드 API로 전송하거나 로컬에서 확인할 수 있도록 구성되어 있습니다.

---

## 🧱 기술 스택

| 항목           | 내용                     |
| -------------- | ------------------------ |
| 언어           | Python 3.x               |
| 웹 크롤링      | Selenium, BeautifulSoup4 |
| 스케줄링       | schedule                 |
| 환경 변수 관리 | python-dotenv            |
| 로깅           | Python logging           |

---

## 📁 디렉토리 구조

```bash
bulbak-crawler/
├── sources/               # 포털별 크롤링 모듈
│   ├── realtime_selenium.py
│   └── ...
├── scheduler/             # 스케줄링 실행 엔진
│   ├── runner.py          # 전체 스케줄 실행 루프
│   ├── registry.py        # 크롤러별 실행 시간 등록
│   └── jobs/              # 크롤러 실행 래퍼
│       ├── realtime.py
│       └── ...
├── utils/                 # 공통 유틸
│   ├── config.py          # 환경 변수 로딩
│   ├── api.py             # API 연동 유틸
│   └── __init__.py
├── .env                  # 환경변수 설정
├── requirements.txt      # 패키지 목록
├── README.md             # 프로젝트 설명 파일
└── main.py               # (선택) 테스트 실행 진입점
```

---

## ⚙️ 환경 설정

### 1. .env 파일 설정

```env
# 필수 환경 변수
FIRST_URL=https://realtime.kr/realtime/
BASE_API_URL=http://localhost:3000/api
CRAWL_INTERVAL_MINUTES=1
```

### 2. Chrome 드라이버 설치

크롤러는 Selenium을 사용하므로 Chrome 드라이버가 필요합니다:

- [ChromeDriver 다운로드](https://sites.google.com/chromium.org/driver/)
- 시스템 PATH에 ChromeDriver 추가

---

## 🚀 실행 방법

### 1. 가상환경 설정

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 실행 방법

#### A. 패키지로 설치하여 실행 (권장)

```bash
# 1. 패키지 설치 (최초 1회만 실행)
pip install -e .

# 2. 실행
bulbak-crawler
```

이 방법은 어느 디렉토리에서든 `bulbak-crawler` 명령어로 실행할 수 있습니다.

#### B. 직접 실행

```bash
# 방법 1: PYTHONPATH 설정하여 실행
PYTHONPATH=$PYTHONPATH:. python scheduler/runner.py

# 방법 2: Python 모듈로 실행
python -m scheduler.runner
```

> 개별 크롤러만 실행하려면 `scheduler/jobs/*.py`에서 직접 `run()` 함수 호출 가능

---

## 📊 로그 확인

모든 로그는 콘솔과 파일로 동시에 출력됩니다.

- 각 크롤러용 로그 파일은 별도 지정 가능 (ex. `crawler.log`, `scheduler.log` 등)

---

## ✅ 크롤링 예시 결과

```
[INFO] 2025-04-19 22:30:00 - 크롤링을 시작합니다...
[INFO] 2025-04-19 22:30:03 - daum에서 10개의 키워드를 수집했습니다.
[INFO] 2025-04-19 22:30:03 - zum에서 10개의 키워드를 수집했습니다.
...
```

---

## 🛠️ 주요 기능

- 멀티 크롤러 등록 및 스케줄 실행 분리
- Selenium 기반 웹 크롤링
- 자동 스케줄링 처리 (`schedule.every(...)`)
- 환경 변수 기반 설정 관리
- 콘솔 + 파일 동시 로그 처리
- 크롤링 결과 자동 DB 저장 (API 연동)

---

## 🧠 향후 개발 계획

- [x] 실시간 키워드 Selenium 기반 수집 구현
- [x] 자동 스케줄링 시스템 구현
- [x] 상세 로깅 시스템 구현
- [x] NestJS API 연동 POST 전송
- [ ] 크롤링 결과 DB 저장 및 중복 필터링
- [ ] 관리자 대시보드 연동
- [ ] GPT 기반 콘텐츠 자동 작성

---

## ⚠️ 주의사항

1. ChromeDriver가 설치되어 있어야 합니다.
2. `.env` 파일에 필수 환경 변수가 설정되어 있어야 합니다.
3. 크롤링 대상 사이트의 robots.txt를 준수해야 합니다.
4. 과도한 크롤링은 IP 차단의 원인이 될 수 있습니다.

---

> "자동화는 정확한 수집에서 시작된다." — Bulbak Crawler

## 기능

- 외교부 채용정보 사이트에서 채용공고 크롤링
- HWP 파일 다운로드 및 텍스트 추출
- 크롤링 결과를 백엔드 API로 전송

## 설치 방법

1. 저장소 클론

```bash
git clone https://github.com/your-username/bulbak-crawler.git
cd bulbak-crawler
```

2. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
.\venv\Scripts\activate  # Windows
```

3. 의존성 설치

```bash
pip install -r requirements.txt
```

4. HWP 처리 도구 설치

```bash
# macOS
brew install hwp5html

# Ubuntu/Debian
sudo apt-get install hwp5html

# Windows
# https://github.com/hancom/hwp5html/releases 에서 다운로드 후 PATH에 추가
```

## 사용 방법

1. 환경 변수 설정

```bash
cp .env.example .env
# .env 파일을 수정하여 필요한 설정을 입력
```

2. 크롤러 실행

```bash
python sources/mofjab_selenium.py
```

## 주요 기능 설명

### HWP 파일 처리

- `hwp5html` 도구를 사용하여 HWP 파일을 HTML로 변환
- BeautifulSoup을 사용하여 HTML에서 텍스트 추출
- 추출된 텍스트는 정리되어 저장됨

### 크롤링 프로세스

1. 외교부 채용정보 사이트에서 채용공고 목록 수집
2. 각 공고의 상세 페이지 방문
3. HWP 파일이 있는 경우 다운로드 및 텍스트 추출
4. 추출된 데이터를 백엔드 API로 전송

## 파일 구조

```
bulbak-crawler/
├── sources/
│   └── mofjab_selenium.py  # 외교부 채용정보 크롤러
├── utils/
│   ├── api.py              # API 통신 모듈
│   ├── config.py           # 설정 파일
│   └── hwp_processor.py    # HWP 파일 처리 모듈
├── downloads/              # 다운로드된 HWP 파일 저장
├── conversion_temp/        # HWP 변환 임시 파일 저장
├── requirements.txt        # Python 의존성
└── README.md              # 프로젝트 설명
```

## 주의사항

- HWP 파일 처리를 위해서는 `hwp5html` 도구가 시스템에 설치되어 있어야 합니다.
- 크롤링 시 서버 부하를 고려하여 적절한 간격을 두고 실행하세요.
- 채용공고의 저작권을 존중하여 수집된 데이터는 적절하게 사용하세요.

## 라이선스

MIT License

# Finviz Map 캡처 및 Google Drive 업로드

이 프로그램은 Finviz의 시장 맵을 자동으로 캡처하여 Google Drive에 업로드합니다.

## 설치 방법

1. 필요한 패키지 설치:
```bash
pip install -r requirements.txt
```

## Google Cloud 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. Google Drive API 활성화
4. 서비스 계정 생성:
   - IAM & 관리 > 서비스 계정 메뉴로 이동
   - "서비스 계정 만들기" 클릭
   - 서비스 계정 세부정보 입력
   - 역할: "편집자" 선택
   - 완료 후 키 생성 (JSON 형식)
5. 다운로드 받은 JSON 키 파일을 프로젝트 루트 디렉토리에 `credentials.json`으로 저장

## Google Drive 설정

1. Google Drive에서 스크린샷을 저장할 폴더 생성
2. 폴더 URL에서 폴더 ID 복사 (URL의 마지막 부분)
3. `sources/finviz_selenium.py` 파일의 `FOLDER_ID` 변수에 복사한 ID 입력

## 실행 방법

```bash
python sources/finviz_selenium.py
```

## 주의사항

- 프로그램이 정상적으로 실행되려면 Chrome 브라우저가 설치되어 있어야 합니다.
- 처음 실행 시 Chrome WebDriver가 자동으로 설치됩니다.
- Google Drive API 할당량에 주의하세요.
