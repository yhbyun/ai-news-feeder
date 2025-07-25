import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# .env 파일에서 이메일 정보와 비밀번호를 가져옵니다.
# main.py와 동일한 환경 변수 이름을 사용합니다.
sender_email = os.getenv("SMTP_USER")
# 쉼표로 구분된 여러 이메일 주소를 리스트로 변환
receiver_emails = [email.strip() for email in os.getenv("RECIPIENT_EMAIL", "").split(',') if email.strip()]
password = os.getenv("SMTP_PASSWORD")
sender_name = os.getenv("SENDER_NAME", "AI 뉴스 알리미") # 보내는 사람 이름

# 환경 변수가 제대로 로드되었는지 확인합니다.
if not all([sender_email, receiver_emails, password]):
    print("오류: .env 파일에 SMTP_USER, RECIPIENT_EMAIL, SMTP_PASSWORD가 모두 설정되어 있는지 확인해주세요.")
    exit()

subject = "Test Email from test.py"
body = "This is a test email with a non-breaking space: \xa0" # Contains \xa0

try:
    # Gmail의 SMTP 서버를 사용하여 SSL 연결을 통해 이메일을 보냅니다.
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, password)
        
        for receiver_email in receiver_emails:
            # UTF-8 인코딩으로 MIMEText 객체를 생성합니다.
            msg = MIMEText(body, 'plain', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = formataddr((str(Header(sender_name, 'utf-8')), sender_email))
            msg['To'] = receiver_email
            smtp.send_message(msg)
            print(f"테스트 이메일이 성공적으로 {receiver_email} 주소로 발송되었습니다!")

except Exception as e:
    print(f"이메일 발송 중 오류가 발생했습니다: {e}")