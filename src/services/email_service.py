import smtplib
import time
import hashlib
import hmac
import base64
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from typing import List
from ..config.settings import Settings
from ..utils.logger import get_logger
from ..utils.exceptions import EmailSendError

logger = get_logger(__name__)

class EmailService:
    """이메일 발송을 담당하는 서비스 클래스"""

    def __init__(self, settings: Settings):
        self.settings = settings

    def send_news_email(self, html_content: str, subject: str) -> None:
        """생성된 HTML을 모든 수신자에게 이메일로 발송합니다."""
        if not self.settings.recipient_emails:
            logger.warning("수신자 이메일이 설정되지 않아 이메일을 발송하지 않습니다.")
            return

        logger.info(f"'{self.settings.email_sender_type}' 방법을 사용하여 이메일 발송을 시작합니다...")

        try:
            if self.settings.email_sender_type == 'smtp':
                self._send_smtp_email(html_content, subject)
            elif self.settings.email_sender_type == 'ncloud':
                self._send_ncloud_email(html_content, subject)
            else:
                raise EmailSendError(f"지원하지 않는 이메일 발송 타입입니다: {self.settings.email_sender_type}")
        except Exception as e:
            logger.error(f"이메일 발송 중 오류 발생: {e}")
            raise EmailSendError(f"이메일 발송 실패: {e}")

    def _send_smtp_email(self, html_content: str, subject: str):
        """SMTP를 사용하여 이메일을 발송합니다."""
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port) as server:
            server.starttls()
            server.login(self.settings.smtp_user, self.settings.smtp_password)

            for recipient_email in self.settings.recipient_emails:
                msg = self._create_smtp_message(html_content, subject, recipient_email)
                server.sendmail(self.settings.smtp_user, recipient_email, msg.as_string())
                logger.info(f"SMTP 이메일이 성공적으로 {recipient_email} 주소로 발송되었습니다.")

    def _create_smtp_message(self, html_content: str, subject: str, recipient_email: str) -> MIMEMultipart:
        """SMTP 이메일 메시지를 생성합니다."""
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((str(Header(self.settings.sender_name, 'utf-8')), self.settings.smtp_user))
        msg['To'] = recipient_email
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))
        return msg

    def _send_ncloud_email(self, html_content: str, subject: str):
        """Naver Cloud Outbound Mailer를 사용하여 이메일을 발송합니다."""
        url = "https://mail.apigw.ntruss.com/api/v1/mails"
        headers = self._get_ncloud_headers()
        
        recipients = [{"address": email, "type": "R"} for email in self.settings.recipient_emails]
        
        payload = {
            "senderAddress": self.settings.ncloud_sender_address,
            "title": subject,
            "body": html_content,
            "recipients": recipients,
            "individual": True,
        }

        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 201:
            logger.info("Ncloud 이메일이 성공적으로 발송 요청되었습니다.")
        else:
            raise EmailSendError(f"Ncloud 이메일 발송 실패: {response.status_code} {response.text}")

    def _get_ncloud_headers(self) -> dict:
        """Naver Cloud API 요청에 필요한 헤더를 생성합니다."""
        timestamp = str(int(time.time() * 1000))
        access_key = self.settings.ncloud_access_key
        secret_key = self.settings.ncloud_secret_key

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
