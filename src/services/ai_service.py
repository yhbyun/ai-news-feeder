from typing import List, Dict, Any
import json
import google.generativeai as genai
from ..models.article import Article
from ..utils.logger import get_logger
from ..utils.exceptions import AIProcessingError

logger = get_logger(__name__)

class AIService:
    """AI 처리를 담당하는 서비스 클래스"""

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-lite')

    def process_article(self, article: Article) -> Article:
        """뉴스 기사를 AI로 처리합니다: 제목 번역, 요약, 태그 추출."""
        logger.info(f"'{article.title}' 뉴스 처리 시작...")

        prompt = f"""
        Analyze the following news article and provide a response in JSON format.
        The JSON object must contain three fields: 'korean_title', 'summary', and 'tags'.
        1.  'korean_title': Translate the original English title into natural Korean.
        2.  'summary': Summarize the article's content in Korean. The summary should be concise and easy for a general audience to understand.
        3.  'tags': Extract 2-3 most relevant keywords (tags) from the article in Korean. The tags should be provided as a list of strings.

        Original Title: {article.title}
        Article Content: {article.description}
        """

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            result = json.loads(json_text)

            # Article 객체 업데이트
            article.korean_title = result.get('korean_title', article.title)
            article.summary = result.get('summary', '요약 생성에 실패했습니다.')
            article.tags = result.get('tags', [])

            logger.info("뉴스 처리 완료.")
            return article

        except (Exception, json.JSONDecodeError) as e:
            logger.error(f"Gemini API 호출 또는 JSON 파싱 중 오류 발생: {e}")
            # 기본값으로 설정
            article.korean_title = article.title
            article.summary = "요약 생성에 실패했습니다."
            article.tags = []
            return article

    def categorize_articles(self, articles: List[Article]) -> List[Dict[str, Any]]:
        """뉴스 기사들을 카테고리별로 분류합니다."""
        logger.info("전체 뉴스를 기반으로 동적 카테고리 생성을 시작합니다...")

        # Gemini에 전달할 뉴스 목록 생성
        news_list_for_prompt = []
        for i, article in enumerate(articles):
            tags_str = ', '.join(article.tags) if article.tags else '태그 없음'
            news_list_for_prompt.append(f"{i}: {article.korean_title} (Tags: {tags_str})")

        prompt = f"""
        You are an expert AI news editor. Based on the following list of news articles, please group them into 3-7 relevant categories.

        Follow these rules strictly:
        1. Distribute the articles as evenly as possible across the categories.
        2. A single category MUST NOT contain more than 6 articles.

        Provide the response in JSON format. The JSON object should have a single key "categories".
        The value of "categories" should be a list of objects, where each object represents a category and contains two keys:
        - 'category_name': The name of the category you created (in Korean).
        - 'articles': A list of numbers corresponding to the articles that belong to this category.

        News List:
        {news_list_for_prompt}
        """

        try:
            response = self.model.generate_content(prompt)
            json_text = response.text.strip().replace("```json", "").replace("```", "")
            categorization_result = json.loads(json_text)
            categories = categorization_result.get('categories', [])

            category_names = [cat['category_name'] for cat in categories]
            logger.info(f"동적 카테고리 생성 완료: {category_names}")
            return categories

        except (Exception, json.JSONDecodeError) as e:
            logger.error(f"카테고리 생성 중 오류 발생: {e}")
            # 오류 발생 시, 모든 기사를 '주요 뉴스'라는 단일 카테고리로 묶음
            return [{"category_name": "주요 뉴스", "articles": list(range(len(articles)))}]