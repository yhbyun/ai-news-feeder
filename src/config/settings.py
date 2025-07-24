from dataclasses import dataclass
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# 로컬 테스트용 .env 파일 로드
if 'CI' not in os.environ:
    load_dotenv()

@dataclass
class NewsSourceConfig:
    """뉴스 소스 설정"""
    name: str
    type: str  # 'api', 'rss'
    enabled: bool
    weight: float
    config: Dict[str, Any]

@dataclass
class Settings:
    """애플리케이션 설정을 관리하는 클래스"""

    # API Keys
    news_api_key: str
    gemini_api_key: str

    # Email Settings
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_password: str
    recipient_emails: List[str]
    sender_name: str

    # News Settings
    article_count: int

    # News Sources Configuration
    news_sources: List[NewsSourceConfig] = None

    def __post_init__(self):
        """기본 뉴스 소스 설정"""
        if self.news_sources is None:
            self.news_sources = [
                NewsSourceConfig(
                    name="news_api",
                    type="api",
                    enabled=True,
                    weight=1.0,
                    config={"api_key": self.news_api_key}
                ),
                # RSS 소스 예제들
                NewsSourceConfig(
                    name="techcrunch",
                    type="rss",
                    enabled=False,
                    weight=0.8,
                    config={"url": "https://techcrunch.com/feed/"}
                ),
                NewsSourceConfig(
                    name="venturebeat",
                    type="rss",
                    enabled=False,
                    weight=0.8,
                    config={"url": "https://venturebeat.com/feed/"}
                ),
                # 새로운 RSS 소스 추가 예제
                # NewsSourceConfig(
                #     name="your_rss_source",
                #     type="rss",
                #     enabled=True,
                #     weight=0.9,
                #     config={"url": "https://your-rss-feed-url.com/feed/"}
                # ),
            ]

    @classmethod
    def from_env(cls) -> 'Settings':
        """환경 변수에서 설정을 로드합니다."""
        return cls(
            news_api_key=os.getenv("NEWS_API_KEY", ""),
            gemini_api_key=os.getenv("GEMINI_API_KEY", ""),
            smtp_host=os.getenv("SMTP_HOST", ""),
            smtp_port=int(os.getenv("SMTP_PORT", "587")),
            smtp_user=os.getenv("SMTP_USER", ""),
            smtp_password=os.getenv("SMTP_PASSWORD", ""),
            recipient_emails=[email.strip() for email in os.getenv("RECIPIENT_EMAIL", "").split(',') if email.strip()],
            sender_name=os.getenv("SENDER_NAME", "AI 뉴스 알리미"),
            article_count=int(os.getenv("NEWS_ARTICLE_COUNT", "5"))
        )

    def validate(self) -> bool:
        """필수 설정값들이 올바르게 설정되었는지 검증합니다."""
        required_fields = [
            self.news_api_key,
            self.gemini_api_key,
            self.smtp_host,
            self.smtp_user,
            self.smtp_password
        ]

        if not all(required_fields):
            return False

        if not self.recipient_emails:
            return False

        return True

    def get_enabled_sources(self) -> List[NewsSourceConfig]:
        """활성화된 뉴스 소스 목록을 반환합니다."""
        return [source for source in self.news_sources if source.enabled]

    def enable_source(self, source_name: str) -> None:
        """뉴스 소스를 활성화합니다."""
        for source in self.news_sources:
            if source.name == source_name:
                source.enabled = True
                break

    def disable_source(self, source_name: str) -> None:
        """뉴스 소스를 비활성화합니다."""
        for source in self.news_sources:
            if source.name == source_name:
                source.enabled = False
                break

    def add_rss_source(self, name: str, url: str, weight: float = 1.0, enabled: bool = True) -> None:
        """새로운 RSS 소스를 추가합니다."""
        new_source = NewsSourceConfig(
            name=name,
            type="rss",
            enabled=enabled,
            weight=weight,
            config={"url": url}
        )
        self.news_sources.append(new_source)

    def add_api_source(self, name: str, api_key: str, weight: float = 1.0, enabled: bool = True) -> None:
        """새로운 API 소스를 추가합니다."""
        new_source = NewsSourceConfig(
            name=name,
            type="api",
            enabled=enabled,
            weight=weight,
            config={"api_key": api_key}
        )
        self.news_sources.append(new_source)