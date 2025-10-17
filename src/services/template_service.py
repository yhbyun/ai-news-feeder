import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from jinja2 import Environment, FileSystemLoader
from premailer import transform
from ..models.article import Article
from ..utils.logger import get_logger
from ..utils.exceptions import TemplateError

logger = get_logger(__name__)

class TemplateService:
    """템플릿 처리를 담당하는 서비스 클래스"""

    def __init__(self):
        self.template_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'templates')
        self.env = Environment(loader=FileSystemLoader(self.template_dir))

    def generate_email_html(self, articles: List[Article], categories: List[Dict[str, Any]], template_name: str) -> Tuple[str, str]:
        """뉴스 데이터와 카테고리를 기반으로 최종 이메일 HTML을 생성합니다."""
        logger.info(f"'{template_name}' 템플릿을 사용하여 이메일 HTML 생성을 시작합니다...")

        today_str = datetime.now().strftime('%Y년 %m월 %d일')
        subject = f"🤖 오늘의 AI 뉴스 ({today_str})"

        try:
            template = self.env.get_template(template_name)

            # 템플릿에 전달할 데이터
            template_data = {
                "subject": subject,
                "categories": categories,
                "processed_articles": [article.to_dict() for article in articles]
            }

            # HTML 렌더링
            html_content = template.render(template_data)

            # CSS 인라이닝
            final_html = transform(html_content, base_path=self.template_dir, allow_loading_external_files=True)

            logger.info("이메일 HTML 생성 완료.")
            return final_html, subject

        except Exception as e:
            logger.error(f"템플릿 처리 중 오류 발생: {e}")
            raise TemplateError(f"이메일 HTML 생성 실패: {e}")