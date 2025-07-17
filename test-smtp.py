import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# .env 파일에서 이메일 정보와 비밀번호를 가져옵니다.
# main.py와 동일한 환경 변수 이름을 사용합니다.
sender_email = os.getenv("SMTP_USER")
receiver_email = os.getenv("RECIPIENT_EMAIL")
password = os.getenv("SMTP_PASSWORD")

# 환경 변수가 제대로 로드되었는지 확인합니다.
if not all([sender_email, receiver_email, password]):
    print("오류: .env 파일에 SMTP_USER, RECIPIENT_EMAIL, SMTP_PASSWORD가 모두 설정되어 있는지 확인해주세요.")
    exit()

subject = "Test Email from test.py"
body = "This is a test email with a non-breaking space: \xa0" # Contains \xa0

# UTF-8 인코딩으로 MIMEText 객체를 생성합니다.
msg = MIMEText(body, 'plain', 'utf-8')
msg['Subject'] = subject
msg['From'] = sender_email
msg['To'] = receiver_email

try:
    # Gmail의 SMTP 서버를 사용하여 SSL 연결을 통해 이메일을 보냅니다.
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, password)
        smtp.send_message(msg)
    print("테스트 이메일이 성공적으로 발송되었습니다!")
except Exception as e:
    print(f"이메일 발송 중 오류가 발생했습니다: {e}")