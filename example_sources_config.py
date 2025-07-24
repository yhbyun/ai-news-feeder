"""
다중 뉴스 소스 설정 예제

이 파일은 다양한 뉴스 소스를 추가하는 방법을 보여줍니다.
실제 사용 시에는 .env 파일에 API 키들을 설정하세요.
"""

from src.config.settings import Settings, NewsSourceConfig

def create_multi_source_settings() -> Settings:
    """다중 뉴스 소스가 포함된 설정을 생성합니다."""

    # 기본 설정 로드
    settings = Settings.from_env()

    # 뉴스 소스 설정
    settings.news_sources = [
        # News API (기본)
        NewsSourceConfig(
            name="news_api",
            type="api",
            enabled=True,
            weight=1.0,
            config={"api_key": settings.news_api_key}
        ),

        # TechCrunch RSS
        NewsSourceConfig(
            name="techcrunch",
            type="rss",
            enabled=True,
            weight=0.9,
            config={"url": "https://techcrunch.com/feed/"}
        ),

        # VentureBeat RSS
        NewsSourceConfig(
            name="venturebeat",
            type="rss",
            enabled=True,
            weight=0.8,
            config={"url": "https://venturebeat.com/feed/"}
        ),

        # MIT Technology Review RSS
        NewsSourceConfig(
            name="mit_tech_review",
            type="rss",
            enabled=False,  # 필요시 True로 변경
            weight=1.1,
            config={"url": "https://www.technologyreview.com/feed/"}
        ),

        # Wired RSS
        NewsSourceConfig(
            name="wired",
            type="rss",
            enabled=False,  # 필요시 True로 변경
            weight=0.7,
            config={"url": "https://www.wired.com/feed/rss"}
        ),

        # Ars Technica RSS
        NewsSourceConfig(
            name="ars_technica",
            type="rss",
            enabled=False,  # 필요시 True로 변경
            weight=0.8,
            config={"url": "https://feeds.arstechnica.com/arstechnica/index"}
        )
    ]

    return settings

def enable_rss_sources(settings: Settings) -> None:
    """RSS 소스들을 활성화합니다."""
    rss_sources = ["techcrunch", "venturebeat", "mit_tech_review", "wired", "ars_technica"]

    for source_name in rss_sources:
        settings.enable_source(source_name)
        print(f"✅ {source_name} 소스가 활성화되었습니다.")

def disable_rss_sources(settings: Settings) -> None:
    """RSS 소스들을 비활성화합니다."""
    rss_sources = ["techcrunch", "venturebeat", "mit_tech_review", "wired", "ars_technica"]

    for source_name in rss_sources:
        settings.disable_source(source_name)
        print(f"❌ {source_name} 소스가 비활성화되었습니다.")

if __name__ == "__main__":
    # 설정 생성
    settings = create_multi_source_settings()

    print("=== 다중 뉴스 소스 설정 예제 ===")
    print(f"총 소스 수: {len(settings.news_sources)}")
    print(f"활성화된 소스: {len(settings.get_enabled_sources())}")

    print("\n활성화된 소스 목록:")
    for source in settings.get_enabled_sources():
        print(f"  - {source.name} ({source.type}, 가중치: {source.weight})")

    print("\n사용법:")
    print("1. enable_rss_sources(settings) - RSS 소스 활성화")
    print("2. disable_rss_sources(settings) - RSS 소스 비활성화")