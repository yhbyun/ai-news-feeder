# 📰 새로운 뉴스 소스 추가 가이드

AI News Feeder에 새로운 뉴스 소스를 추가하는 방법을 설명합니다.

## 🚀 빠른 시작

### 1. RSS 소스 추가 (가장 쉬운 방법)

#### 방법 1: 설정에서 직접 추가

`src/config/settings.py` 파일의 `__post_init__` 메서드에서 주석 처리된 예제를 참고하여 추가:

```python
# 새로운 RSS 소스 추가 예제
NewsSourceConfig(
    name="your_rss_source",
    type="rss",
    enabled=True,
    weight=0.9,
    config={"url": "https://your-rss-feed-url.com/feed/"}
),
```

#### 방법 2: 코드에서 동적 추가

```python
from src.config.settings import Settings

# 설정 로드
settings = Settings.from_env()

# 새로운 RSS 소스 추가
settings.add_rss_source(
    name="my_tech_blog",
    url="https://mytechblog.com/feed/",
    weight=0.8,
    enabled=True
)
```

### 2. API 소스 추가

```python
from src.config.settings import Settings

# 설정 로드
settings = Settings.from_env()

# 새로운 API 소스 추가
settings.add_api_source(
    name="my_news_api",
    api_key="your_api_key_here",
    weight=1.0,
    enabled=True
)
```

## 📋 지원하는 RSS 소스 예제

### 기술 뉴스
- **TechCrunch**: `https://techcrunch.com/feed/`
- **VentureBeat**: `https://venturebeat.com/feed/`
- **Ars Technica**: `https://feeds.arstechnica.com/arstechnica/index`
- **The Verge**: `https://www.theverge.com/rss/index.xml`

### AI/ML 전문
- **MIT Technology Review**: `https://www.technologyreview.com/feed/`
- **AI News**: `https://artificialintelligence-news.com/feed/`
- **Machine Learning Mastery**: `https://machinelearningmastery.com/feed/`

### 일반 뉴스
- **Reuters Technology**: `https://feeds.reuters.com/reuters/technology`
- **BBC Technology**: `https://feeds.bbci.co.uk/news/technology/rss.xml`
- **Wired**: `https://www.wired.com/feed/rss`

## 🔧 설정 옵션

### 가중치 (Weight)
- **1.0 이상**: 높은 우선순위 (Reuters, MIT Tech Review 등)
- **0.8-0.9**: 중간 우선순위 (TechCrunch, VentureBeat 등)
- **0.7 이하**: 낮은 우선순위 (개인 블로그 등)

### 활성화/비활성화
```python
# 소스 활성화
settings.enable_source("techcrunch")

# 소스 비활성화
settings.disable_source("wired")
```

## 🧪 테스트 방법

### 1. 개별 소스 테스트
```python
from src.services.news_sources.rss_source import RSSSource

# RSS 소스 테스트
rss_source = RSSSource(
    name="Test RSS",
    url="https://techcrunch.com/feed/",
    weight=1.0
)

# 뉴스 가져오기 테스트
articles = rss_source.fetch_news(
    keywords=["AI", "Machine Learning"],
    date_from="2024-01-01"
)

print(f"수집된 뉴스: {len(articles)}개")
for article in articles[:3]:
    print(f"- {article.title}")
```

### 2. 전체 시스템 테스트
```python
from src.services.news_service import NewsService
from src.config.settings import Settings

# 설정 로드
settings = Settings.from_env()

# 새 소스 추가
settings.add_rss_source("test_source", "https://techcrunch.com/feed/")

# 뉴스 서비스 생성
news_service = NewsService(settings)

# 뉴스 수집 테스트
articles = news_service.fetch_ai_news()
print(f"총 {len(articles)}개의 뉴스 수집 완료")
```

## ⚠️ 주의사항

### RSS 피드 품질
- **유효한 RSS URL**: RSS 피드가 올바른 형식인지 확인
- **업데이트 빈도**: 너무 오래된 피드는 제외
- **콘텐츠 품질**: AI 관련 키워드가 포함된 피드 우선

### API 제한
- **요청 제한**: API 호출 횟수 제한 확인
- **비용**: 유료 API의 경우 비용 고려
- **안정성**: 서비스 가용성 확인

### 성능 최적화
- **병렬 처리**: 여러 소스에서 동시에 뉴스 수집
- **캐싱**: 중복 요청 방지
- **타임아웃**: 네트워크 지연 대응

## 🔍 문제 해결

### RSS 피드 오류
```python
# 피드 유효성 검사
import feedparser

feed = feedparser.parse("https://example.com/feed/")
if feed.bozo:
    print(f"RSS 피드 오류: {feed.bozo_exception}")
else:
    print(f"유효한 RSS 피드: {len(feed.entries)}개 항목")
```

### API 키 오류
```python
# API 키 유효성 검사
import requests

response = requests.get("https://api.example.com/test",
                       headers={"Authorization": "Bearer your_api_key"})
if response.status_code == 401:
    print("API 키가 유효하지 않습니다.")
```

## 📝 예제 스크립트

### RSS 소스 일괄 추가
```python
# add_rss_sources.py
from src.config.settings import Settings

def add_popular_rss_sources():
    settings = Settings.from_env()

    rss_sources = [
        ("techcrunch", "https://techcrunch.com/feed/", 0.9),
        ("venturebeat", "https://venturebeat.com/feed/", 0.8),
        ("mit_tech_review", "https://www.technologyreview.com/feed/", 1.1),
        ("wired", "https://www.wired.com/feed/rss", 0.7),
        ("ars_technica", "https://feeds.arstechnica.com/arstechnica/index", 0.8),
    ]

    for name, url, weight in rss_sources:
        settings.add_rss_source(name, url, weight, enabled=True)
        print(f"✅ {name} RSS 소스 추가됨")

    return settings

if __name__ == "__main__":
    settings = add_popular_rss_sources()
    print(f"총 {len(settings.news_sources)}개의 소스 설정 완료")
```

이제 새로운 뉴스 소스를 쉽게 추가할 수 있습니다! 🎯