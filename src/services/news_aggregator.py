from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
from ..models.article import Article
from ..services.news_sources.base import NewsSource
from ..utils.logger import get_logger
from ..utils.exceptions import NewsFetchError

logger = get_logger(__name__)

class NewsAggregator:
    """여러 뉴스 소스를 통합하고 집계하는 서비스"""

    def __init__(self, sources: List[NewsSource]):
        self.sources = sources
        self.keywords = [
            '"Artificial Intelligence"', '"Machine Learning"', 'LLM',
            'OpenAI', 'ChatGPT', 'Sora',
            'Google', 'Gemini',
            'Anthropic', 'Claude',
            'Meta', 'Llama',
            'Perplexity', 'Cursor', 'Midjourney'
        ]

    def aggregate_news(self, max_articles: int = 10) -> List[Article]:
        """모든 활성화된 소스에서 뉴스를 수집하고 집계합니다."""
        logger.info("뉴스 집계를 시작합니다...")

        all_articles = []

        # 각 소스에서 뉴스 수집
        for source in self.sources:
            if not source.is_enabled():
                logger.info(f"{source.get_source_name()} 소스가 비활성화되어 있습니다.")
                continue

            try:
                date_from = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                articles = source.fetch_news(self.keywords, date_from)

                # 가중치 적용
                for article in articles:
                    article.weight = source.get_weight()

                all_articles.extend(articles)
                logger.info(f"{source.get_source_name()}에서 {len(articles)}개 뉴스 수집 완료")

            except NewsFetchError as e:
                logger.error(f"{source.get_source_name()}에서 뉴스 수집 실패: {e}")
                continue
            except Exception as e:
                logger.error(f"{source.get_source_name()}에서 예상치 못한 오류: {e}")
                continue

        if not all_articles:
            logger.warning("수집된 뉴스가 없습니다.")
            return []

        # 중복 제거 및 품질 점수 계산
        unique_articles = self._remove_duplicates(all_articles)
        scored_articles = self._calculate_quality_scores(unique_articles)

        # 상위 기사 선택
        top_articles = sorted(scored_articles, key=lambda x: x.quality_score, reverse=True)[:max_articles]

        logger.info(f"총 {len(top_articles)}개의 뉴스를 최종 선택했습니다.")
        return top_articles

    def _remove_duplicates(self, articles: List[Article]) -> List[Article]:
        """URL 기반 중복 제거"""
        seen_urls = set()
        unique_articles = []

        for article in articles:
            url = article.url
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

        logger.info(f"중복 제거: {len(articles)}개 → {len(unique_articles)}개")
        return unique_articles

    def _calculate_quality_scores(self, articles: List[Article]) -> List[Article]:
        """뉴스 품질 점수 계산"""
        now = datetime.now(timezone.utc)  # UTC 시간으로 통일

        for article in articles:
            score = 0

            # 출처별 가중치
            source_weights = {
                'reuters': 1.2,
                'techcrunch': 1.1,
                'venturebeat': 1.0,
                'wired': 0.9,
                'mit technology review': 1.1,
                'news api': 1.0,
                '네이버 뉴스': 1.1,  # 네이버 뉴스 가중치 추가
            }

            source_name = article.source_name.lower()
            score += source_weights.get(source_name, 0.8)

            # 제목 길이 점수
            title_length = len(article.title)
            if 20 <= title_length <= 100:
                score += 0.3

            # 요약 길이 점수
            summary_length = len(article.description)
            if 100 <= summary_length <= 500:
                score += 0.2

            # 최신성 점수
            if article.published_at:
                try:
                    # timezone-naive datetime을 UTC로 변환
                    if article.published_at.tzinfo is None:
                        published_at_utc = article.published_at.replace(tzinfo=timezone.utc)
                    else:
                        published_at_utc = article.published_at.astimezone(timezone.utc)

                    days_old = (now - published_at_utc).days
                    if days_old <= 1:
                        score += 0.5
                    elif days_old <= 3:
                        score += 0.3
                    elif days_old <= 7:
                        score += 0.1
                except Exception as e:
                    logger.warning(f"날짜 계산 중 오류: {e}")
                    # 날짜 계산 실패 시 기본 점수만 부여
                    pass

            article.quality_score = score

        return articles