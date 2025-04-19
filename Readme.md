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
├── venv/                  # Python 가상환경
├── sources/               # 포털별 수집기 모듈
│   └── adfirst_selenium.py # Selenium 기반 크롤러
├── utils/                 # 공통 유틸
│   ├── __init__.py
│   └── config.py         # 환경 변수 관리
├── main.py               # 메인 실행 진입점
├── scheduler.py          # 일정 기반 실행 관리
├── .env                  # 환경변수 설정
├── requirements.txt      # 패키지 목록
├── crawler.log          # 크롤러 로그
├── scheduler.log        # 스케줄러 로그
└── README.md            # 프로젝트 설명 파일
```

---

## ⚙️ 환경 설정

### 1. .env 파일 설정

```env
# 필수 환경 변수
FIRST_URL=http://localhost:3000/api   # 크롤링 대상 URL
CRAWL_INTERVAL_MINUTES=30             # 크롤링 주기 (분)
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

#### 단일 실행

```bash
python main.py
```

#### 스케줄러 실행 (주기적 크롤링)

```bash
python scheduler.py
```

---

## 📊 로그 확인

크롤러는 두 가지 로그 파일을 생성합니다:

1. `crawler.log`: 크롤링 작업 관련 로그
2. `scheduler.log`: 스케줄러 실행 관련 로그

로그는 콘솔과 파일에 동시에 출력됩니다.

---

## ✅ 크롤링 예시 결과

```
[INFO] 2024-04-19 14:30:00 - 크롤링을 시작합니다...
[INFO] 2024-04-19 14:30:03 - daum에서 10개의 키워드를 수집했습니다.
[INFO] 2024-04-19 14:30:03 - zum에서 10개의 키워드를 수집했습니다.
[INFO] 2024-04-19 14:30:03 - nate에서 10개의 키워드를 수집했습니다.
[INFO] 2024-04-19 14:30:03 - googletrend에서 10개의 키워드를 수집했습니다.
[INFO] 2024-04-19 14:30:03 - 크롤링이 완료되었습니다.
```

---

## 🛠️ 주요 기능

- Selenium 기반 웹 크롤링
- 자동 스케줄링
- 상세 로깅
- 환경 변수 기반 설정
- 예외 처리 및 에러 복구
- 리소스 자동 정리

---

## 🧠 향후 개발 계획

- [x] 실시간 키워드 Selenium 기반 수집 구현
- [x] 자동 스케줄링 시스템 구현
- [x] 상세 로깅 시스템 구현
- [ ] NestJS API 연동 POST 전송
- [ ] 크롤링 결과 DB 저장 및 중복 필터링
- [ ] 관리자 대시보드 연동

---

## ⚠️ 주의사항

1. ChromeDriver가 설치되어 있어야 합니다.
2. `.env` 파일에 필수 환경 변수가 설정되어 있어야 합니다.
3. 크롤링 대상 사이트의 robots.txt를 준수해야 합니다.
4. 과도한 크롤링은 IP 차단의 원인이 될 수 있습니다.

---

> "자동화는 정확한 수집에서 시작된다." — Bulbak Crawler
