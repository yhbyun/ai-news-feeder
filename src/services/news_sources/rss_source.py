import feedparser
from datetime import datetime
from typing import List
from .base import NewsSource
from ...models.article import Article
from ...utils.logger import get_logger
from ...utils.exceptions import NewsFetchError

logger = get_logger(__name__)

class RSSSource(NewsSource):
    """RSS 피드를 사용하는 뉴스 소스"""

    def __init__(self, name: str, url: str, weight: float = 1.0, keywords: List[str] = None):
        super().__init__(name, weight)
        self.url = url
        self.keywords = keywords or []

    def get_source_name(self) -> str:
        return self.name

    def fetch_news(self, keywords: List[str], date_from: str) -> List[Article]:
        """RSS 피드에서 뉴스를 가져옵니다."""
        logger.info(f"{self.name}에서 뉴스 수집을 시작합니다...")

        try:
            feed = feedparser.parse(self.url)

            if feed.bozo:
                logger.warning(f"{self.name} RSS 피드 파싱 오류: {feed.bozo_exception}")

            articles = []
            for entry in feed.entries:
                # 키워드 필터링
                if self._contains_keywords(entry.title + " " + entry.summary, keywords):
                    article = self._create_article_from_entry(entry)
                    articles.append(article)

            logger.info(f"{self.name}에서 총 {len(articles)}개의 뉴스를 발견했습니다.")
            return articles

        except Exception as e:
            logger.error(f"{self.name} RSS 피드 처리 중 오류: {e}")
            raise NewsFetchError(f"{self.name} 뉴스 수집 실패: {e}")

    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        """텍스트에 키워드가 포함되어 있는지 확인합니다."""
        if not keywords:
            return True

        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        return False

    def _create_article_from_entry(self, entry) -> Article:
        """RSS 엔트리에서 Article 객체를 생성합니다."""
        # published_at 파싱
        published_at = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except (ValueError, TypeError):
                pass

        return Article(
            title=entry.title,
            description=entry.summary,
            url=entry.link,
            source_name=self.name,
            source_id=self.name.lower().replace(' ', '_'),
            published_at=published_at
        )