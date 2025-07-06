import openai
import json
import time
import logging
import os
from dotenv import load_dotenv
from utils.api import get_nasdaq_stocks, post_stock_mapping, get_sp500_stocks

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# ✅ OpenAI API 키를 환경 변수에서 가져오기
openai.api_key = os.getenv('OPENAI_API_KEY')
if not openai.api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

def fetch_us_companies():
    logging.info("나스닥 종목 목록을 가져오는 중...")
    companies = get_nasdaq_stocks()
    logging.info(f"총 {len(companies)}개의 나스닥 종목을 가져왔습니다.")
    return companies

def ask_gpt_for_korea_mapping(us_symbol, us_name):
    logging.info(f"GPT에 {us_symbol} ({us_name}) 관련 국내 종목 매핑 요청 중...")
    prompt = f"""
미국 주식 {us_symbol} ({us_name})과 관련된 한국 주식 종목 20개를 찾아 JSON 배열로만 반환해라.
코드 블록(```)을 사용하지 말고, 순수 JSON 배열만 반환하세요.

──────────────────
📌 선정 기준
1. 사업 영역 유사성  
   • 두 기업이 속한 **세부 산업**(예: 파운드리, SaaS, 2차전지 소재)이 동일·유사한가?  
   • 최근 연간 매출 비중(%)이나 주력 제품이 겹치는지 명시.

2. 공급망 연관성  
   • 한국 기업이 美 기업의 **직·간접 부품·소재·장비·서비스 공급사**(또는 역으로 공급받는 입장)인가?  
   • 최근 3년 내 납품 계약·수출입 실적(가능하면 금액·기간)을 근거로 제시.

3. 경쟁 관계  
   • 글로벌/국내 시장에서 **동일 제품·서비스**로 시장 점유율 경쟁 중인가?  
   • 주요 경쟁 지표(점유율 %, 출하량, MAU 등)와 경쟁 구도(1위 vs 2위 등)를 1줄로 요약.

4. 기술 유사성 / 기술 제휴  
   • **공동 연구·특허 라이선스·MOU·합작 공장** 또는 **동일 핵심 기술**(예: GAA 2 nm, LLM, SiC 전력반도체)을 보유?  
   • 최근 5년 내 발표·로드맵·로열티 계약 유무를 포함.

5. 글로벌 투자 테마  
   • 두 기업이 **같은 메가트렌드**(AI, 반도체, 전기차, 친환경, 바이오, 클라우드 등)에 속하며  
   • 정부 정책·ETF 편입·기관 리포트 등 **테마 근거**가 있는가?

──────────────────
📌 결과 작성 규칙
• 총 20개: **"POSITIVE"** 10개, **"NEGATIVE"** 10개.  
• KOSPI·KOSDAQ 비율을 가능하면 골고루.  
• `reason` 필드는 위 5가지 기준 중 **가장 설득력 있는 1–2가지**만 120자 이내로 요약(출처 표기는 제외).  
• 동일 기업·중복 이유 금지.  
• 아래 예시 형식을 반드시 지키고, 다른 설명·주석·텍스트는 절대 출력하지 말 것.

[
  {{
    "krName": "삼성전자",
    "krSymbol": "005930",
    "reason": "파운드리 시장 2위 vs 1위 TSMC, 글로벌 점유율 17% 차지",
    "marketType": "KOSPI",
    "correlationType": "POSITIVE"
  }}
]

위 예시처럼 marketType은 반드시 "KOSPI" 또는 "KOSDAQ" 중 하나여야 하며,
correlationType은 반드시 "POSITIVE" 또는 "NEGATIVE" 중 하나여야 함.
"""
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # GPT-4O-MINI 모델 사용
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4
    )
    content = response.choices[0].message.content.strip()
    
    # Remove code block markers if present
    if content.startswith('```'):
        content = content.split('```')[1] if '```' in content else content
    if content.startswith('json'):
        content = content[4:].strip()
    
    logging.info(f"GPT 응답 수신 완료: {us_symbol}")
    logging.info(f"GPT 응답 내용: {content}")
    
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logging.error(f"JSON 파싱 오류: {str(e)}")
        logging.error(f"파싱 실패한 응답: {content}")
        raise

def save_mapping(us_symbol, mapping_list, is_sp500=False):
    market_type = "S&P 500" if is_sp500 else "나스닥"
    logging.info(f"{market_type} 종목 {us_symbol}의 {len(mapping_list)}개 매핑 데이터 저장 중...")
    
    for item in mapping_list:
        if "marketType" not in item:
            logging.warning(f"{us_symbol} → {item['krName']} : marketType 누락! 기본값 'KOSPI'로 저장")
            item["marketType"] = "KOSPI"
        
        payload = {
            "krName": item["krName"],
            "krSymbol": item["krSymbol"],
            "reason": item["reason"],
            "marketType": item["marketType"],
            "correlationType": item["correlationType"]
        }
        
        logging.info(f"API로 전송할 payload 상세 정보:")
        logging.info(f"- Symbol: {us_symbol}")
        logging.info(f"- Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        post_stock_mapping(us_symbol, payload, is_sp500)
        logging.info(f"[✔] {us_symbol} → {item['krName']} ({item['krSymbol']}, {item['marketType']}) 저장 완료")

def main():
    logging.info("매핑 프로세스 시작")
    
    # S&P 500 종목만 처리
    logging.info("S&P 500 종목 처리 시작")
    sp500_companies = get_sp500_stocks()
    process_companies(sp500_companies, is_sp500=True)
    logging.info("S&P 500 종목 처리 완료")
    
    logging.info("모든 매핑 프로세스 완료")

def process_companies(companies, is_sp500=False):
    market_type = "S&P 500" if is_sp500 else "나스닥"
    total = len(companies)
    
    for idx, company in enumerate(companies, 1):
        symbol = company["symbol"]
        name = company["name"]
        logging.info(f"\n[{idx}/{total}] {market_type} 종목 {symbol} ({name}) 처리 중...")

        try:
            gpt_response = ask_gpt_for_korea_mapping(symbol, name)
            logging.info(f"{symbol}에 대한 {len(gpt_response)}개 매핑 데이터 수신")

            save_mapping(symbol, gpt_response, is_sp500)
            logging.info(f"{symbol} 처리 완료. 3초 대기 중...")
            time.sleep(3)  # GPT API rate limit 회피
        except Exception as e:
            logging.error(f"❌ 오류 발생 - {symbol}: {str(e)}")

if __name__ == "__main__":
    main() 