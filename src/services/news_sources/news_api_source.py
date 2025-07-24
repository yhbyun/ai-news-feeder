import requests
from datetime import datetime, timedelta
from typing import List
from .base import NewsSource
from ...models.article import Article
from ...utils.logger import get_logger
from ...utils.exceptions import NewsFetchError

logger = get_logger(__name__)

class NewsAPISource(NewsSource):
    """News API를 사용하는 뉴스 소스"""

    def __init__(self, api_key: str, weight: float = 1.0):
        super().__init__("News API", weight)
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"

    def get_source_name(self) -> str:
        return self.name

    def fetch_news(self, keywords: List[str], date_from: str) -> List[Article]:
        """News API를 통해 AI 관련 최신 뉴스를 가져옵니다."""
        logger.info(f"{self.name}에서 뉴스 수집을 시작합니다...")

        query = " OR ".join(keywords)

        params = {
            'q': f"({query})",
            'from': date_from,
            'sortBy': 'popularity',
            'language': 'en',
            'apiKey': self.api_key
        }

        logger.info(f"뉴스 검색어: {query}")

        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()
            articles_data = data.get("articles", [])
            logger.info(f"{self.name}에서 총 {len(articles_data)}개의 뉴스를 발견했습니다.")

            # Article 객체로 변환
            articles = []
            for article_data in articles_data:
                article = self._create_article_from_data(article_data)
                articles.append(article)

            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"{self.name} API 요청 중 오류 발생: {e}")
            raise NewsFetchError(f"{self.name} 뉴스 수집 실패: {e}")
        except Exception as e:
            logger.error(f"{self.name} 처리 중 예상치 못한 오류: {e}")
            raise NewsFetchError(f"{self.name} 처리 실패: {e}")

    def _create_article_from_data(self, article_data: dict) -> Article:
        """API 응답 데이터에서 Article 객체를 생성합니다."""
        source = article_data.get('source', {})

        # published_at 파싱
        published_at = None
        if article_data.get('publishedAt'):
            try:
                published_at = datetime.fromisoformat(article_data['publishedAt'].replace('Z', '+00:00'))
            except ValueError:
                pass

        return Article(
            title=article_data.get('title', ''),
            description=article_data.get('description', '') or article_data.get('content', ''),
            url=article_data.get('url', ''),
            source_name=source.get('name', 'Unknown'),
            source_id=source.get('id', ''),
            published_at=published_at
        )