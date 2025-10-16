import os
import time
import hashlib
import hmac
import base64
import requests
from dotenv import load_dotenv

# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# .env 파일에서 Naver Cloud API 정보를 가져옵니다.
access_key = os.getenv("NCLOUD_ACCESS_KEY")
secret_key = os.getenv("NCLOUD_SECRET_KEY")
sender_address = os.getenv("NCLOUD_SENDER_ADDRESS")
receiver_emails = [email.strip() for email in os.getenv("RECIPIENT_EMAIL", "").split(',') if email.strip()]

# 환경 변수가 제대로 로드되었는지 확인합니다.
if not all([access_key, secret_key, sender_address, receiver_emails]):
    print("오류: .env 파일에 NCLOUD_ACCESS_KEY, NCLOUD_SECRET_KEY, NCLOUD_SENDER_ADDRESS, RECIPIENT_EMAIL이 모두 설정되어 있는지 확인해주세요.")
    exit()

subject = "Test Email from test-ncloud.py"
body = "This is a test email sent via Naver Cloud Outbound Mailer."

def get_ncloud_headers(access_key, secret_key):
    """Naver Cloud API 요청에 필요한 헤더를 생성합니다."""
    timestamp = str(int(time.time() * 1000))
    method = "POST"
    uri = "/api/v1/mails"

    message = f"{method} {uri}\n{timestamp}\n{access_key}"
    signature = hmac.new(secret_key.encode('utf-8'), message.encode('utf-8'), hashlib.sha256).digest()
    signature_b64 = base64.b64encode(signature).decode('utf-8')

    return {
        "Content-Type": "application/json",
        "x-ncp-apigw-timestamp": timestamp,
        "x-ncp-iam-access-key": access_key,
        "x-ncp-apigw-signature-v2": signature_b64
    }

try:
    url = "https://mail.apigw.ntruss.com/api/v1/mails"
    headers = get_ncloud_headers(access_key, secret_key)

    recipients = [{"address": email, "type": "R"} for email in receiver_emails]

    payload = {
        "senderAddress": sender_address,
        "title": subject,
        "body": body,
        "recipients": recipients,
        "individual": True,
        "advertising": False,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 201:
        print("테스트 이메일이 성공적으로 발송 요청되었습니다!")
        print(f"수신자: {', '.join(receiver_emails)}")
    else:
        print(f"이메일 발송 요청 실패: {response.status_code}")
        print(f"응답 내용: {response.text}")

except Exception as e:
    print(f"이메일 발송 중 오류가 발생했습니다: {e}")
