#!/usr/bin/env python3
"""
네이버 뉴스 소스들을 일괄 추가하는 스크립트
"""

from src.config.settings import Settings

def add_naver_news_sources():
    """네이버 뉴스 소스들을 추가합니다."""
    settings = Settings.from_env()

    # 네이버 뉴스 카테고리별 소스들
    naver_sources = [
        ("naver_it", "it", 1.0),           # IT/과학
        ("naver_economy", "economy", 0.8),  # 경제
        ("naver_society", "society", 0.7),  # 사회
        ("naver_politics", "politics", 0.6), # 정치
    ]

    print("🤖 네이버 뉴스 소스 추가 중...")

    for name, category, weight in naver_sources:
        # 이미 존재하는 소스인지 확인
        existing_source = next((s for s in settings.news_sources if s.name == name), None)

        if existing_source:
            print(f"⚠️  {name} 소스가 이미 존재합니다. 건너뜁니다.")
        else:
            settings.add_naver_source(name, category, weight, enabled=False)  # 기본적으로 비활성화
            print(f"✅ {name} 네이버 뉴스 소스 추가됨 (카테고리: {category}, 가중치: {weight})")

    print(f"\n📊 총 {len(settings.news_sources)}개의 소스 설정 완료")
    print("\n🔧 활성화하려면:")
    for source in settings.news_sources:
        if source.type == "naver" and not source.enabled:
            print(f"   settings.enable_source('{source.name}')")

    return settings

def enable_all_naver_sources():
    """모든 네이버 뉴스 소스를 활성화합니다."""
    settings = Settings.from_env()

    print("🔌 모든 네이버 뉴스 소스 활성화 중...")

    for source in settings.news_sources:
        if source.type == "naver":
            source.enabled = True
            print(f"✅ {source.name} 활성화됨")

    return settings

def disable_all_naver_sources():
    """모든 네이버 뉴스 소스를 비활성화합니다."""
    settings = Settings.from_env()

    print("🔌 모든 네이버 뉴스 소스 비활성화 중...")

    for source in settings.news_sources:
        if source.type == "naver":
            source.enabled = False
            print(f"❌ {source.name} 비활성화됨")

    return settings

def test_naver_source():
    """네이버 뉴스 소스를 테스트합니다."""
    from src.services.news_sources.naver_news_source import NaverNewsSource

    print("🧪 네이버 뉴스 소스 테스트 중...")

    # IT 카테고리 테스트
    source = NaverNewsSource("naver_it", "it", weight=1.0)

    try:
        articles = source.fetch_news(["AI", "인공지능"], "2024-01-01")
        print(f"✅ 네이버 IT 뉴스 수집 성공: {len(articles)}개")

        for i, article in enumerate(articles[:3], 1):
            print(f"  {i}. {article.title}")
            print(f"     URL: {article.url}")
            print(f"     출처: {article.source_name}")
            print()

    except Exception as e:
        print(f"❌ 네이버 뉴스 테스트 실패: {e}")

def list_naver_sources():
    """네이버 뉴스 소스 목록을 표시합니다."""
    settings = Settings.from_env()

    print("📰 현재 설정된 네이버 뉴스 소스:")
    print("-" * 50)

    naver_sources = [s for s in settings.news_sources if s.type == "naver"]

    if not naver_sources:
        print("설정된 네이버 뉴스 소스가 없습니다.")
        return

    for i, source in enumerate(naver_sources, 1):
        status = "🟢 활성화" if source.enabled else "🔴 비활성화"
        category = source.config.get("category", "unknown")
        print(f"{i}. {source.name} (카테고리: {category}) - {status} (가중치: {source.weight})")

    print("-" * 50)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "add":
            add_naver_news_sources()
        elif command == "enable":
            enable_all_naver_sources()
        elif command == "disable":
            disable_all_naver_sources()
        elif command == "test":
            test_naver_source()
        elif command == "list":
            list_naver_sources()
        else:
            print("사용법: python add_naver_sources.py [add|enable|disable|test|list]")
    else:
        print("🤖 네이버 뉴스 소스 관리 스크립트")
        print("\n사용법:")
        print("  python add_naver_sources.py add     - 네이버 뉴스 소스 추가")
        print("  python add_naver_sources.py enable  - 모든 네이버 소스 활성화")
        print("  python add_naver_sources.py disable - 모든 네이버 소스 비활성화")
        print("  python add_naver_sources.py test    - 네이버 소스 테스트")
        print("  python add_naver_sources.py list    - 네이버 소스 목록 표시")