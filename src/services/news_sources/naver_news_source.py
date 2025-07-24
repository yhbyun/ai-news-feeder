import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from typing import List
import re
from .base import NewsSource
from ...models.article import Article
from ...utils.logger import get_logger
from ...utils.exceptions import NewsFetchError

logger = get_logger(__name__)

class NaverNewsSource(NewsSource):
    """네이버 뉴스를 사용하는 뉴스 소스"""

    def __init__(self, name: str, category: str, weight: float = 1.0):
        super().__init__(name, weight)
        self.category = category
        self.base_url = "https://news.naver.com"

        # 카테고리별 URL 매핑
        self.category_urls = {
            "it": "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=105",
            "economy": "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=101",
            "society": "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=102",
            "politics": "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100"
        }

        # AI 관련 한국어 키워드
        self.ai_keywords = [
            "인공지능", "AI", "머신러닝", "딥러닝",
            "챗GPT", "오픈AI", "OpenAI", "구글", "제미니", "Gemini",
            "메타", "Meta", "라마", "Llama", "앤트로픽", "Anthropic", "클로드", "Claude",
            "로봇", "자율주행", "빅데이터", "블록체인",
            "4차 산업혁명", "디지털 전환", "스마트팩토리", "메타버스"
        ]

    def get_source_name(self) -> str:
        return f"네이버 뉴스 ({self.category})"

    def fetch_news(self, keywords: List[str], date_from: str) -> List[Article]:
        """네이버 뉴스에서 AI 관련 뉴스를 가져옵니다."""
        logger.info(f"{self.name}에서 뉴스 수집을 시작합니다...")

        try:
            url = self.category_urls.get(self.category, self.category_urls["it"])
            response = requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # 다양한 뉴스 링크 패턴 시도
            link_patterns = [
                'a[href*="/main/read.naver"]',
                'a[href*="/article/"]',
                '.news_area a',
                '.list_area a',
                '.main_component a'
            ]

            news_links = []
            for pattern in link_patterns:
                links = soup.select(pattern)
                if links:
                    news_links.extend(links)
                    break

            # 링크가 없으면 일반적인 링크 찾기
            if not news_links:
                news_links = soup.find_all('a', href=True)

            logger.info(f"발견된 링크 수: {len(news_links)}")

            for link in news_links[:30]:  # 상위 30개 링크 처리
                try:
                    article = self._extract_article_from_link(link)
                    if article and self._contains_ai_keywords(article.title + " " + article.description):
                        articles.append(article)
                        logger.info(f"AI 관련 뉴스 발견: {article.title}")
                except Exception as e:
                    logger.warning(f"뉴스 추출 중 오류: {e}")
                    continue

            logger.info(f"{self.name}에서 총 {len(articles)}개의 AI 관련 뉴스를 발견했습니다.")
            return articles

        except Exception as e:
            logger.error(f"{self.name} 뉴스 수집 중 오류: {e}")
            raise NewsFetchError(f"{self.name} 뉴스 수집 실패: {e}")

    def _extract_article_from_link(self, link) -> Article:
        """뉴스 링크에서 기사 정보를 추출합니다."""
        title = link.get_text(strip=True)
        if not title or len(title) < 10:  # 너무 짧은 제목 제외
            return None

        href = link.get('href', '')
        if not href:
            return None

        # URL 정규화
        if href.startswith('/'):
            url = self.base_url + href
        elif href.startswith('http'):
            url = href
        else:
            url = self.base_url + '/' + href

        # 간단한 설명 생성
        description = f"{title} - 네이버 뉴스에서 제공하는 최신 정보입니다."

        # timezone-aware datetime 생성
        published_at = datetime.now(timezone.utc)

        return Article(
            title=title,
            description=description,
            url=url,
            source_name=self.get_source_name(),
            source_id=f"naver_{self.category}",
            published_at=published_at
        )

    def _contains_ai_keywords(self, text: str) -> bool:
        """텍스트에 AI 관련 키워드가 포함되어 있는지 확인합니다."""
        text_lower = text.lower()
        for keyword in self.ai_keywords:
            if keyword.lower() in text_lower:
                return True
        return False