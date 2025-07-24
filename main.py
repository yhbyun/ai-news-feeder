import sys
from src.config.settings import Settings
from src.services.news_service import NewsService
from src.services.ai_service import AIService
from src.services.template_service import TemplateService
from src.services.email_service import EmailService
from src.utils.logger import get_logger
from src.utils.exceptions import NewsFetchError, AIProcessingError, EmailSendError, ConfigurationError

logger = get_logger(__name__)

def generate_mock_data():
    """미리보기용 샘플 데이터를 생성합니다."""
    from src.models.article import Article

    logger.info("미리보기용 샘플 데이터를 생성합니다...")

    mock_articles = [
        Article(
            title="샘플 뉴스 1: AI의 미래",
            description="이것은 첫 번째 샘플 뉴스의 요약입니다.",
            url="#",
            source_name="TechCrunch",
            source_id="techcrunch",
            korean_title="샘플 뉴스 1: AI의 미래",
            summary="이것은 첫 번째 샘플 뉴스의 요약입니다.",
            tags=["AI", "미래 기술"]
        ),
        Article(
            title="샘플 뉴스 2: 머신러닝의 발전",
            description="두 번째 샘플 뉴스는 머신러닝에 대한 내용입니다.",
            url="#",
            source_name="VentureBeat",
            source_id="venturebeat",
            korean_title="샘플 뉴스 2: 머신러닝의 발전",
            summary="두 번째 샘플 뉴스는 머신러닝에 대한 내용입니다.",
            tags=["머신러닝", "기술 동향"]
        ),
        Article(
            title="샘플 뉴스 3: 새로운 AI 모델 출시",
            description="세 번째 샘플 뉴스는 새로운 모델 출시에 대한 소식입니다.",
            url="#",
            source_name="Reuters",
            source_id="reuters",
            korean_title="샘플 뉴스 3: 새로운 AI 모델 출시",
            summary="세 번째 샘플 뉴스는 새로운 모델 출시에 대한 소식입니다.",
            tags=["신제품", "AI 모델"]
        ),
        Article(
            title="샘플 뉴스 4: AI와 윤리",
            description="네 번째 샘플 뉴스는 AI의 윤리적 문제에 대해 다룹니다.",
            url="#",
            source_name="MIT Technology Review",
            source_id="mit",
            korean_title="샘플 뉴스 4: AI와 윤리",
            summary="네 번째 샘플 뉴스는 AI의 윤리적 문제에 대해 다룹니다.",
            tags=["AI 윤리", "정책"]
        ),
        Article(
            title="샘플 뉴스 5: 데이터 과학의 중요성",
            description="다섯 번째 샘플 뉴스는 데이터 과학의 중요성을 강조합니다.",
            url="#",
            source_name="Wired",
            source_id="wired",
            korean_title="샘플 뉴스 5: 데이터 과학의 중요성",
            summary="다섯 번째 샘플 뉴스는 데이터 과학의 중요성을 강조합니다.",
            tags=["데이터 과학", "분석"]
        ),
    ]

    categories = [
        {'category_name': '기술 및 미래', 'articles': [0, 1]},
        {'category_name': '제품 및 정책', 'articles': [2, 3]},
        {'category_name': '기타', 'articles': [4]}
    ]

    return mock_articles, categories

def main():
    """스크립트의 메인 실행 함수"""
    try:
        # 설정 로드 및 검증
        settings = Settings.from_env()
        if not settings.validate():
            logger.error("필수 설정값이 누락되었습니다.")
            sys.exit(1)

        # 미리보기 모드 확인
        if '--preview' in sys.argv:
            mock_articles, categories = generate_mock_data()
            template_service = TemplateService()
            html_content, subject = template_service.generate_preview_html(mock_articles, categories)

            preview_file = "email_preview.html"
            with open(preview_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"이메일 미리보기가 '{preview_file}' 파일로 저장되었습니다.")
            return

        # 서비스 초기화
        news_service = NewsService(settings)
        ai_service = AIService(settings.gemini_api_key)
        template_service = TemplateService()
        email_service = EmailService(settings)

        # 1. 뉴스 수집
        articles = news_service.fetch_ai_news()

        if not articles:
            logger.warning("처리할 뉴스가 없습니다.")
            return

        # 2. AI 처리 (요약, 번역, 태그 추출)
        processed_articles = []
        for article in articles:
            try:
                processed_article = ai_service.process_article(article)
                processed_articles.append(processed_article)
            except AIProcessingError as e:
                logger.error(f"뉴스 처리 중 오류: {e}")
                # 오류가 발생해도 계속 진행
                processed_articles.append(article)

        # 3. 카테고리 분류
        try:
            categories = ai_service.categorize_articles(processed_articles)
        except AIProcessingError as e:
            logger.error(f"카테고리 분류 중 오류: {e}")
            # 기본 카테고리 사용
            categories = [{"category_name": "주요 뉴스", "articles": list(range(len(processed_articles)))}]

        # 4. 이메일 생성 및 발송
        html_content, subject = template_service.generate_email_html(processed_articles, categories)
        email_service.send_news_email(html_content, subject)

        logger.info("AI 뉴스 피더 작업이 성공적으로 완료되었습니다.")

    except ConfigurationError as e:
        logger.error(f"설정 오류: {e}")
        sys.exit(1)
    except NewsFetchError as e:
        logger.error(f"뉴스 수집 오류: {e}")
        sys.exit(1)
    except AIProcessingError as e:
        logger.error(f"AI 처리 오류: {e}")
        sys.exit(1)
    except EmailSendError as e:
        logger.error(f"이메일 발송 오류: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"예상치 못한 오류 발생: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()