#!/usr/bin/env python3
"""
인기 있는 RSS 소스들을 일괄 추가하는 스크립트
"""

from src.config.settings import Settings

def add_popular_rss_sources():
    """인기 있는 RSS 소스들을 추가합니다."""
    settings = Settings.from_env()

    # 인기 있는 기술 뉴스 RSS 소스들
    rss_sources = [
        ("techcrunch", "https://techcrunch.com/feed/", 0.9),
        ("venturebeat", "https://venturebeat.com/feed/", 0.8),
        ("mit_tech_review", "https://www.technologyreview.com/feed/", 1.1),
        ("wired", "https://www.wired.com/feed/rss", 0.7),
        ("ars_technica", "https://feeds.arstechnica.com/arstechnica/index", 0.8),
        ("the_verge", "https://www.theverge.com/rss/index.xml", 0.8),
        ("reuters_tech", "https://feeds.reuters.com/reuters/technology", 1.0),
        ("bbc_tech", "https://feeds.bbci.co.uk/news/technology/rss.xml", 0.9),
    ]

    print("🤖 인기 RSS 소스 추가 중...")

    for name, url, weight in rss_sources:
        # 이미 존재하는 소스인지 확인
        existing_source = next((s for s in settings.news_sources if s.name == name), None)

        if existing_source:
            print(f"⚠️  {name} 소스가 이미 존재합니다. 건너뜁니다.")
        else:
            settings.add_rss_source(name, url, weight, enabled=False)  # 기본적으로 비활성화
            print(f"✅ {name} RSS 소스 추가됨 (가중치: {weight})")

    print(f"\n📊 총 {len(settings.news_sources)}개의 소스 설정 완료")
    print("\n🔧 활성화하려면:")
    for source in settings.news_sources:
        if source.type == "rss" and not source.enabled:
            print(f"   settings.enable_source('{source.name}')")

    return settings

def enable_all_rss_sources():
    """모든 RSS 소스를 활성화합니다."""
    settings = Settings.from_env()

    print("🔌 모든 RSS 소스 활성화 중...")

    for source in settings.news_sources:
        if source.type == "rss":
            source.enabled = True
            print(f"✅ {source.name} 활성화됨")

    return settings

def disable_all_rss_sources():
    """모든 RSS 소스를 비활성화합니다."""
    settings = Settings.from_env()

    print("🔌 모든 RSS 소스 비활성화 중...")

    for source in settings.news_sources:
        if source.type == "rss":
            source.enabled = False
            print(f"❌ {source.name} 비활성화됨")

    return settings

def list_sources():
    """현재 설정된 모든 소스를 나열합니다."""
    settings = Settings.from_env()

    print("📰 현재 설정된 뉴스 소스:")
    print("-" * 50)

    for i, source in enumerate(settings.news_sources, 1):
        status = "🟢 활성화" if source.enabled else "🔴 비활성화"
        print(f"{i}. {source.name} ({source.type}) - {status} (가중치: {source.weight})")

    print("-" * 50)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "add":
            add_popular_rss_sources()
        elif command == "enable":
            enable_all_rss_sources()
        elif command == "disable":
            disable_all_rss_sources()
        elif command == "list":
            list_sources()
        else:
            print("사용법: python add_rss_sources.py [add|enable|disable|list]")
    else:
        print("🤖 RSS 소스 관리 스크립트")
        print("\n사용법:")
        print("  python add_rss_sources.py add     - 인기 RSS 소스 추가")
        print("  python add_rss_sources.py enable  - 모든 RSS 소스 활성화")
        print("  python add_rss_sources.py disable - 모든 RSS 소스 비활성화")
        print("  python add_rss_sources.py list    - 현재 소스 목록 표시")