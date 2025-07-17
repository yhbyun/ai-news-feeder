import os
import smtplib
import requests
import google.generativeai as genai
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

# --- 설정 ---
# GitHub Secrets나 .env 파일에서 환경 변수 로드
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SMTP_HOST = os.getenv("SMTP_HOST")  # 예: "smtp.gmail.com"
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")  # 보내는 사람 이메일
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") # 보내는 사람 이메일 비밀번호 또는 앱 비밀번호
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL") # 받는 사람 이메일
ARTICLE_COUNT = int(os.getenv("NEWS_ARTICLE_COUNT", 5)) # 요약할 뉴스 기사 수 (기본값: 5)

# Gemini API 설정
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_ai_news():
    """News API를 통해 AI 관련 최신 뉴스를 가져옵니다."""
    print("AI 뉴스 수집을 시작합니다...")
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    url = (
        "https://newsapi.org/v2/everything?"
        "q=(AI OR Artificial Intelligence OR machine learning OR LLM OR OpenAI OR Google DeepMind)&"
        f"from={yesterday}&"
        "sortBy=popularity&"
        "language=en&"
        f"apiKey={NEWS_API_KEY}"
    )
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
        return []
    except Exception as e:
        print(f"뉴스 처리 중 알 수 없는 오류 발생: {e}")
        return []

def summarize_with_gemini(article):
    """Gemini API를 사용하여 뉴스 기사를 한국어로 요약합니다."""
    print(f"'{article['title']}' 뉴스 요약을 시작합니다...")
    prompt = f"""
    Please summarize the following news article in KOREAN.
    Focus on the key points and keep it concise and easy to understand for a general audience.

    Article Title: {article.get('title', 'N/A')}
    Article Content: {article.get('description', '') or article.get('content', '')}
    """
    try:
        response = model.generate_content(prompt)
        summary = response.text
        print("뉴스 요약 완료.")
        return summary
    except Exception as e:
        print(f"Gemini API 호출 중 오류 발생: {e}")
        return "요약 생성에 실패했습니다."

def send_email(summaries):
    """요약된 뉴스 내용을 이메일로 발송합니다."""
    if not summaries:
        print("요약된 뉴스가 없어 이메일을 발송하지 않습니다.")
        return

    print("이메일 발송을 시작합니다...")
    today_str = datetime.now().strftime('%Y년 %m월 %d일')
    subject = f"📰 오늘의 AI 뉴스 요약 ({today_str})"

    # 이메일 본문 (HTML)
    html_body = f"<html><head><meta charset='utf-8'></head><body><h2>{subject}</h2>"
    for title, summary, url in summaries:
        # HTML에서 줄바꿈을 위해 \n을 <br>로 변경
        summary_html = summary.replace('\n', '<br>')
        html_body += (
            f"<h3><a href='{url}' target='_blank'>{title}</a></h3>"
            f"<p>{summary_html}</p>"
            "<hr>"
        )
    html_body += "</body></html>"

    msg = MIMEMultipart('alternative')
    msg['From'] = SMTP_USER
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = Header(subject, 'utf-8') # 제목에 UTF-8 인코딩 적용

    # 본문에 UTF-8 인코딩 적용
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, RECIPIENT_EMAIL, msg.as_string())
        print(f"이메일이 성공적으로 {RECIPIENT_EMAIL} 주소로 발송되었습니다.")
    except smtplib.SMTPException as e:
        print(f"이메일 발송 중 오류 발생: {e}")
    except Exception as e:
        print(f"이메일 발송 중 알 수 없는 오류 발생: {e}")


if __name__ == "__main__":
    # 1. 뉴스 가져오기
    articles = get_ai_news()

    # 2. 뉴스 요약하기
    summarized_articles = []
    if articles:
        for article in articles:
            summary = summarize_with_gemini(article)
            summarized_articles.append((article['title'], summary, article['url']))

    # 3. 이메일 보내기
    send_email(summarized_articles)
