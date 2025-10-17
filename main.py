import sys
import time
import argparse
from src.config.settings import Settings
from src.services.news_service import NewsService
from src.services.ai_service import AIService
from src.services.template_service import TemplateService
from src.services.email_service import EmailService
from src.services.teams_service import TeamsService
from src.utils.logger import get_logger
from src.utils.exceptions import NewsFetchError, AIProcessingError, NotificationError, ConfigurationError

logger = get_logger(__name__)

def generate_mock_data():
    """미리보기용 샘플 데이터를 생성합니다."""
    from src.models.article import Article
    # ... (mock data generation code is unchanged)
    mock_articles = [
        Article(
            title="샘플 뉴스 1: AI의 미래",
            description="이것은 첫 번째 샘플 뉴스의 요약입니다.",
            url="http://www.example.com/sample1",
            source_name="TechCrunch",
            source_id="techcrunch",
            korean_title="샘플 뉴스 1: AI의 미래",
            summary="이것은 첫 번째 샘플 뉴스의 요약입니다.",
            tags=["AI", "미래 기술"]
        ),
        Article(
            title="샘플 뉴스 2: 머신러닝의 발전",
            description="두 번째 샘플 뉴스는 머신러닝에 대한 내용입니다.",
            url="http://www.example.com/sample2",
            source_name="VentureBeat",
            source_id="venturebeat",
            korean_title="샘플 뉴스 2: 머신러닝의 발전",
            summary="두 번째 샘플 뉴스는 머신러닝에 대한 내용입니다.",
            tags=["머신러닝", "기술 동향"]
        ),
        Article(
            title="샘플 뉴스 3: 새로운 AI 모델 출시",
            description="세 번째 샘플 뉴스는 새로운 모델 출시에 대한 소식입니다.",
            url="http://www.example.com/sample3",
            source_name="Reuters",
            source_id="reuters",
            korean_title="샘플 뉴스 3: 새로운 AI 모델 출시",
            summary="세 번째 샘플 뉴스는 새로운 모델 출시에 대한 소식입니다.",
            tags=["신제품", "AI 모델"]
        ),
    ]
    categories = [
        {'category_name': '기술 동향', 'articles': [0, 1]},
        {'category_name': '신제품 소식', 'articles': [2]}
    ]
    return mock_articles, categories

def main():
    """스크립트의 메인 실행 함수"""
    parser = argparse.ArgumentParser(description="AI 뉴스 피더")
    parser.add_argument('--notify', type=str, choices=['email', 'teams'], default='email',
                        help="알림을 보낼 방식 (기본값: email)")
    parser.add_argument('--preview', action='store_true',
                        help="실제 발송 대신 이메일 HTML 미리보기를 생성합니다.")
    args = parser.parse_args()

    try:
        # 설정 로드 및 공통 설정 검증
        settings = Settings.from_env()
        if not settings.validate_common():
            raise ConfigurationError("필수 API 키가 누락되었습니다.")

        # 알림 방식에 따른 설정 검증
        if args.notify == 'email':
            if not settings.validate_email_settings():
                raise ConfigurationError("이메일 발송에 필요한 설정이 누락되었습니다.")
        elif args.notify == 'teams':
            if not settings.validate_teams_settings():
                raise ConfigurationError("MS Teams 발송에 필요한 웹훅 URL이 누락되었습니다.")

        # 미리보기 모드 처리
        if args.preview:
            mock_articles, categories = generate_mock_data()

            if args.notify == 'email':
                template_service = TemplateService()
                preview_template = settings.default_email_template
                logger.info(f"'{preview_template}' 템플릿을 사용하여 이메일 미리보기를 생성합니다.")
                html_content, _ = template_service.generate_email_html(mock_articles, categories, preview_template)

                preview_file = "email_preview.html"
                with open(preview_file, "w", encoding="utf-8") as f:
                    f.write(html_content)
                logger.info(f"이메일 미리보기가 '{preview_file}' 파일로 저장되었습니다.")

            elif args.notify == 'teams':
                logger.info("Teams 채널로 미리보기 메시지를 발송합니다...")
                teams_service = TeamsService(settings)
                teams_service.send_news_message(mock_articles, categories)
                logger.info("Teams 미리보기 메시지가 성공적으로 발송되었습니다.")

            return

        # --- 메인 로직 ---
        news_service = NewsService(settings)
        ai_service = AIService(settings.gemini_api_key)

        # 1. 뉴스 수집
        articles = news_service.fetch_ai_news()
        if not articles:
            logger.warning("처리할 뉴스가 없습니다.")
            return

        # 2. AI 처리
        processed_articles = []
        for article in articles:
            try:
                processed_article = ai_service.process_article(article)
                processed_articles.append(processed_article)
                time.sleep(10)
            except AIProcessingError as e:
                logger.error(f"뉴스 처리 중 오류: {e}")
                processed_articles.append(article)

        # 3. 카테고리 분류
        try:
            categories = ai_service.categorize_articles(processed_articles)
        except AIProcessingError as e:
            logger.error(f"카테고리 분류 중 오류: {e}")
            categories = [{"category_name": "주요 뉴스", "articles": list(range(len(processed_articles)))}]

        # 4. 알림 발송
        if args.notify == 'email':
            template_service = TemplateService()
            email_service = EmailService(settings, template_service)
            email_service.send_news_email(processed_articles, categories)
        elif args.notify == 'teams':
            teams_service = TeamsService(settings)
            teams_service.send_news_message(processed_articles, categories)

        logger.info(f"AI 뉴스 피더 작업이 '{args.notify}' 방식으로 성공적으로 완료되었습니다.")

    except ConfigurationError as e:
        logger.error(f"설정 오류: {e}")
        sys.exit(1)
    except (NewsFetchError, AIProcessingError, NotificationError) as e:
        logger.error(f"작업 실행 중 오류: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
