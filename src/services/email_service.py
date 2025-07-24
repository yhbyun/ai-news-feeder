import smtplib
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
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.recipient_emails = settings.recipient_emails
        self.sender_name = settings.sender_name

    def send_news_email(self, html_content: str, subject: str) -> None:
        """생성된 HTML을 모든 수신자에게 이메일로 발송합니다."""
        if not self.recipient_emails:
            logger.warning("수신자 이메일이 설정되지 않아 이메일을 발송하지 않습니다.")
            return

        logger.info("이메일 발송을 시작합니다...")

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)

                for recipient_email in self.recipient_emails:
                    msg = self._create_message(html_content, subject, recipient_email)
                    server.sendmail(self.smtp_user, recipient_email, msg.as_string())
                    logger.info(f"이메일이 성공적으로 {recipient_email} 주소로 발송되었습니다.")

        except Exception as e:
            logger.error(f"이메일 발송 중 오류 발생: {e}")
            raise EmailSendError(f"이메일 발송 실패: {e}")

    def _create_message(self, html_content: str, subject: str, recipient_email: str) -> MIMEMultipart:
        """이메일 메시지를 생성합니다."""
        msg = MIMEMultipart('alternative')
        msg['From'] = formataddr((str(Header(self.sender_name, 'utf-8')), self.smtp_user))
        msg['To'] = recipient_email
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        return msg