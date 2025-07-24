from typing import List
from ..models.article import Article
from ..config.settings import Settings
from ..services.news_sources.news_api_source import NewsAPISource
from ..services.news_sources.rss_source import RSSSource
from ..services.news_aggregator import NewsAggregator
from ..utils.logger import get_logger
from ..utils.exceptions import NewsFetchError

logger = get_logger(__name__)

class NewsService:
    """뉴스 수집을 담당하는 서비스 클래스"""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.article_count = settings.article_count
        self.aggregator = self._create_aggregator(settings)

    def _create_aggregator(self, settings: Settings) -> NewsAggregator:
        """설정에 따라 뉴스 집계기를 생성합니다."""
        sources = []

        for source_config in settings.news_sources:
            if not source_config.enabled:
                continue

            if source_config.type == "api":
                if source_config.name == "news_api":
                    source = NewsAPISource(
                        api_key=source_config.config["api_key"],
                        weight=source_config.weight
                    )
                    sources.append(source)

            elif source_config.type == "rss":
                source = RSSSource(
                    name=source_config.name,
                    url=source_config.config["url"],
                    weight=source_config.weight
                )
                sources.append(source)

        logger.info(f"총 {len(sources)}개의 뉴스 소스가 활성화되었습니다.")
        return NewsAggregator(sources)

    def fetch_ai_news(self) -> List[Article]:
        """AI 관련 최신 뉴스를 가져옵니다."""
        logger.info("AI 뉴스 수집을 시작합니다...")

        try:
            articles = self.aggregator.aggregate_news(max_articles=self.article_count)
            logger.info(f"총 {len(articles)}개의 뉴스를 수집했습니다.")
            return articles

        except Exception as e:
            logger.error(f"뉴스 수집 중 오류 발생: {e}")
            raise NewsFetchError(f"뉴스 수집 실패: {e}")

    def get_source_statistics(self) -> dict:
        """뉴스 소스별 통계를 반환합니다."""
        stats = {
            "total_sources": len(self.aggregator.sources),
            "enabled_sources": len([s for s in self.aggregator.sources if s.is_enabled()]),
            "source_names": [s.get_source_name() for s in self.aggregator.sources if s.is_enabled()]
        }
        return stats