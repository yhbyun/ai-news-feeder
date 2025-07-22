import os
import sys
import smtplib
import requests
import google.generativeai as genai
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from datetime import datetime, timedelta
from collections import defaultdict

# --- 로컬 테스트용 .env 파일 로드 ---
# GitHub Actions 환경에서는 이 부분이 실행되지 않도록 CI 환경 변수 확인
if 'CI' not in os.environ:
    from dotenv import load_dotenv
    load_dotenv()

# --- 설정 ---
# GitHub Secrets나 .env 파일에서 환경 변수 로드
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SMTP_HOST = os.getenv("SMTP_HOST")  # 예: "smtp.gmail.com"
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")  # 보내는 사람 이메일
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # 보내는 사람 이메일 비밀번호 또는 앱 비밀번호
# 쉼표로 구분된 여러 이메일 주소를 리스트로 변환
RECIPIENT_EMAILS = [email.strip() for email in os.getenv("RECIPIENT_EMAIL", "").split(',') if email.strip()]
SENDER_NAME = os.getenv("SENDER_NAME", "AI 뉴스 알리미") # 보내는 사람 이름
ARTICLE_COUNT = int(os.getenv("NEWS_ARTICLE_COUNT", 5)) # 요약할 뉴스 기사 수 (기본값: 5)

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_news():
    """News API를 통해 AI 관련 최신 뉴스를 가져옵니다."""
    print("AI 뉴스 수집을 시작합니다...")
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    # 최신 트렌드를 반영한 검색 키워드
    keywords = [
        '"Artificial Intelligence"', '"Machine Learning"', 'LLM',
        'OpenAI', 'ChatGPT', 'Sora',
        'Google', 'Gemini',
        'Anthropic', 'Claude',
        'Meta', 'Llama',
        'Perplexity', 'Cursor', 'Midjourney'
    ]
    query = " OR ".join(keywords)

    url = (
        "https://newsapi.org/v2/everything?"
        f"q=({query})&"
        f"from={yesterday}&"
        "sortBy=popularity&"
        "language=en&"
        f"apiKey={NEWS_API_KEY}"
    )
    
    print(f"뉴스 검색어: {query}")

    try:
        response = requests.get(url)
        response.raise_for_status()  # HTTP 오류가 발생하면 예외를 발생시킵니다.
        articles = response.json().get("articles", [])
        print(f"총 {len(articles)}개의 뉴스를 발견했습니다.")

        # 설정된 개수만큼 뉴스 반환
        print(f"상위 {ARTICLE_COUNT}개의 뉴스만 처리합니다.")
        return articles[:ARTICLE_COUNT]
    except requests.exceptions.RequestException as e:
        print(f"뉴스 API 요청 중 오류 발생: {e}")
        raise  # 예외를 다시 발생시켜 상위에서 처리하도록 함

def summarize_with_gemini(article):
    """Gemini API를 사용하여 뉴스 기사를 한국어로 요약하고, 제목을 번역하며, 카테고리를 분류합니다."""
    print(f"'{article['title']}' 뉴스 처리 시작...")
    
    prompt = f"""
    Analyze the following news article and provide a response in JSON format.
    The JSON object must contain three fields: 'korean_title', 'summary', and 'category'.
    1.  'korean_title': Translate the original English title into natural Korean.
    2.  'summary': Summarize the article's content in Korean. The summary should be concise and easy for a general audience to understand.
    3.  'category': Classify the article into one of the following categories in Korean: "기술 동향", "산업 및 비즈니스", "정책 및 규제", "연구 및 개발", "기타".

    Original Title: {article.get('title', 'N/A')}
    Article Content: {article.get('description', '') or article.get('content', '')}
    """
    
    try:
        response = model.generate_content(prompt)
        # Gemini 응답에서 JSON 부분만 추출
        json_text = response.text.strip().replace("```json", "").replace("```", "")
        result = json.loads(json_text)
        print("뉴스 처리 완료.")
        return result
    except (Exception, json.JSONDecodeError) as e:
        print(f"Gemini API 호출 또는 JSON 파싱 중 오류 발생: {e}")
        # 실패 시 기본값 반환
        return {
            "korean_title": article.get('title', 'N/A'), # 오류 시 원본 제목 사용
            "summary": "요약 생성에 실패했습니다.",
            "category": "기타"
        }


def send_email(summarized_articles):
    """요약된 뉴스 내용을 카테고리별로 그룹화하여 이메일로 발송합니다."""
    if not summarized_articles:
        print("요약된 뉴스가 없어 이메일을 발송하지 않습니다.")
        return
    if not RECIPIENT_EMAILS:
        print("수신자 이메일이 설정되지 않아 이메일을 발송하지 않습니다.")
        return

    print("이메일 발송을 시작합니다...")
    today_str = datetime.now().strftime('%Y년 %m월 %d일')
    subject = f"📰 오늘의 AI 뉴스 ({today_str})"

    # 카테고리별로 뉴스 그룹화
    articles_by_category = defaultdict(list)
    for article_data in summarized_articles:
        articles_by_category[article_data['category']].append(article_data)

    # 이메일 본문 (HTML)
    html_body = f"<html><head><meta charset='utf-8'></head><body><h2>{subject}</h2>"
    
    # 정의된 카테고리 순서
    category_order = ["기술 동향", "산업 및 비즈니스", "정책 및 규제", "연구 및 개발", "기타"]

    for category in category_order:
        if category in articles_by_category:
            html_body += f"<h3 style='color:#0056b3; border-bottom:2px solid #0056b3; padding-bottom:5px; margin-top:20px;'># {category}</h3>"
            for article_data in articles_by_category[category]:
                summary_html = article_data['summary'].replace('\n', '<br>')
                html_body += (
                    f"<h4 style='margin-bottom:5px;'><a href=\"{article_data['url']}\" target='_blank' style='text-decoration:none; color:#333;'>{article_data['korean_title']}</a></h4>"
                    f"<p style='margin-top:5px; padding-left: 15px; border-left: 3px solid #ccc;'>{summary_html}</p>"
                )
    html_body += "</body></html>"

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)

            for recipient_email in RECIPIENT_EMAILS:
                msg = MIMEMultipart('alternative')
                msg['From'] = formataddr((str(Header(SENDER_NAME, 'utf-8')), SMTP_USER))
                msg['To'] = recipient_email
                msg['Subject'] = Header(subject, 'utf-8')
                msg.attach(MIMEText(html_body, 'html', 'utf-8'))

                server.sendmail(SMTP_USER, recipient_email, msg.as_string())
                print(f"이메일이 성공적으로 {recipient_email} 주소로 발송되었습니다.")

    except Exception as e:
        print(f"이메일 발송 중 오류 발생: {e}")
        raise

def main():
    """스크립트의 메인 실행 함수"""
    try:
        # 1. 뉴스 가져오기
        articles = get_ai_news()

        # 2. 뉴스 요약, 번역 및 분류
        summarized_articles = []
        if articles:
            for article in articles:
                processed_data = summarize_with_gemini(article)
                processed_data['url'] = article['url']
                summarized_articles.append(processed_data)

        # 3. 이메일 보내기
        send_email(summarized_articles)

        print("AI 뉴스 피더 작업이 성공적으로 완료되었습니다.")

    except Exception as e:
        # 스크립트 실행 중 처리되지 않은 예외가 발생하면 오류 메시지를 출력하고 실패 코드로 종료
        print(f"스크립트 실행 중 심각한 오류가 발생했습니다: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()