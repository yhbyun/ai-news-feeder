# AI News Feeder 🤖

AI 관련 뉴스를 수집, 요약, 번역하고 이메일로 전송하는 자동화 시스템입니다.

## ✨ 주요 기능

- **다중 뉴스 소스 지원**: News API, RSS 피드 등 다양한 소스에서 뉴스 수집
- **AI 기반 처리**: Google Gemini를 활용한 제목 번역, 요약, 태그 추출
- **동적 카테고리 분류**: AI가 뉴스 내용을 분석하여 자동으로 카테고리 분류
- **품질 기반 선별**: 출처, 최신성, 내용 품질을 고려한 뉴스 선별
- **중복 제거**: URL 기반 중복 뉴스 자동 제거
- **이메일 발송**: HTML 템플릿을 활용한 깔끔한 이메일 발송

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/yhbyun/ai-news-feeder.git
cd ai-news-feeder

# 의존성 설치
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# API Keys
NEWS_API_KEY=your_news_api_key
GEMINI_API_KEY=your_gemini_api_key

# Email Settings
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient1@example.com,recipient2@example.com
SENDER_NAME=AI 뉴스 알리미

# News Settings
NEWS_ARTICLE_COUNT=5
```

### 3. 실행

```bash
python main.py
```

## 📰 뉴스 소스 설정

### 기본 소스 (News API)
- **활성화**: 기본적으로 활성화됨
- **가중치**: 1.0
- **설정**: NEWS_API_KEY 환경 변수 필요

### RSS 소스 추가

`example_sources_config.py` 파일을 참고하여 RSS 소스를 추가할 수 있습니다:

```python
from src.config.settings import Settings, NewsSourceConfig

# RSS 소스 활성화
settings.enable_source("techcrunch")
settings.enable_source("venturebeat")
```

### 지원하는 RSS 소스

- **TechCrunch**: `https://techcrunch.com/feed/`
- **VentureBeat**: `https://venturebeat.com/feed/`
- **MIT Technology Review**: `https://www.technologyreview.com/feed/`
- **Wired**: `https://www.wired.com/feed/rss`
- **Ars Technica**: `https://feeds.arstechnica.com/arstechnica/index`

## 🏗️ 아키텍처

```
src/
├── config/
│   └── settings.py          # 설정 관리
├── models/
│   └── article.py           # 뉴스 기사 모델
├── services/
│   ├── news_sources/        # 뉴스 소스 모듈
│   │   ├── base.py         # 추상 클래스
│   │   ├── news_api_source.py
│   │   └── rss_source.py
│   ├── news_aggregator.py  # 뉴스 집계
│   ├── news_service.py     # 뉴스 서비스
│   ├── ai_service.py       # AI 처리
│   ├── template_service.py # 템플릿 생성
│   └── email_service.py    # 이메일 발송
└── utils/
    ├── logger.py           # 로깅
    └── exceptions.py       # 예외 처리
```

## 🔧 설정 옵션

### 뉴스 소스 관리

```python
# 소스 활성화/비활성화
settings.enable_source("techcrunch")
settings.disable_source("wired")

# 가중치 조정
for source in settings.news_sources:
    if source.name == "techcrunch":
        source.weight = 1.2  # 더 높은 우선순위
```

### 품질 점수 시스템

뉴스 기사는 다음 요소로 품질 점수가 계산됩니다:

- **출처 신뢰도**: Reuters(1.2), TechCrunch(1.1) 등
- **제목 품질**: 적절한 길이(20-100자)
- **요약 품질**: 적절한 길이(100-500자)
- **최신성**: 1일 이내(0.5), 3일 이내(0.3), 7일 이내(0.1)

## 📧 이메일 템플릿

이메일은 다음과 같은 구조로 발송됩니다:

- **제목**: 🤖 오늘의 AI 뉴스 (날짜)
- **카테고리별 분류**: AI가 자동으로 분류한 카테고리
- **기사 정보**: 한국어 제목, 요약, 태그, 출처
- **반응형 디자인**: 모바일 친화적 레이아웃

## 🚀 배포

### GitHub Actions (권장)

#### 1. GitHub Secrets 설정

저장소의 **Settings > Secrets and variables > Actions**에서 다음 Secrets를 설정하세요:

**Secrets (민감 정보)**
| Secret 이름 | 설명 | 예시 값 |
|------------|------|---------|
| `NEWS_API_KEY` | News API에서 발급받은 키 | `a1b2c3d4e5f67890...` |
| `GEMINI_API_KEY` | Gemini API에서 발급받은 키 | `AIzaSyA...` |
| `SMTP_HOST` | SMTP 서버 주소 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 포트 번호 | `587` |
| `SMTP_USER` | 발송 이메일 주소 | `your-email@gmail.com` |
| `SMTP_PASSWORD` | 앱 비밀번호 | `abcd efgh ijkl mnop` |

**Variables (설정)**
| Variable 이름 | 설명 | 예시 값 | 기본값 |
|--------------|------|---------|--------|
| `RECIPIENT_EMAIL` | 수신 이메일 주소 (쉼표로 여러개) | `a@a.com,b@b.com` | 없음 |
| `SENDER_NAME` | 발신자 이름 | `AI News` | "AI 뉴스 알리미" |
| `NEWS_ARTICLE_COUNT` | 요약할 뉴스 개수 | `5` | `5` |

#### 2. 앱 비밀번호 생성

보안을 위해 실제 계정 비밀번호 대신 **앱 비밀번호**를 사용하세요:

- **[Gmail 앱 비밀번호 생성](https://support.google.com/accounts/answer/185833)**
- **[Naver 앱 비밀번호 생성](https://help.naver.com/service/5640_5642/19849/2-2.%20%EC%95%B1%20%EB%B9%84%EB%B0%80%EB%B2%88%ED%98%B8%EB%A5%BC%20%EC%84%A4%EC%A0%95%ED%95%B4%EC%9A%94.)**

#### 3. API 키 발급

- **[News API](https://newsapi.org/)** - 뉴스 데이터 제공 (무료 플랜 가능)
- **[Google Gemini](https://ai.google.dev/)** - AI 처리

#### 4. 실행하기

**자동 실행**
- `.github/workflows/main.yml`에 설정된 스케줄에 따라 워크플로우가 자동으로 실행됩니다
- GitHub Actions의 **Actions** 탭에서 실행 로그를 확인할 수 있습니다

**수동 실행**
1. GitHub 저장소의 **Actions** 탭으로 이동
2. **AI News Feeder** 워크플로우 선택
3. **Run workflow** 버튼 클릭
4. 즉시 실행되며 결과를 확인할 수 있습니다

### 로컬 실행

#### 기본 실행
```bash
python main.py
```

#### 이메일 미리보기
```bash
# 이메일 템플릿 미리보기 (실제 발송하지 않음)
python main.py --preview

# 미리보기 파일 생성 후 브라우저에서 열기
python main.py --preview && open email_preview.html
```

#### 스케줄 실행 (cron)
```bash
# crontab 편집
crontab -e

# 매일 오전 9시 실행
0 9 * * * cd /path/to/ai-news-feeder && python main.py

# 매일 오전 9시 실행 (로그 포함)
0 9 * * * cd /path/to/ai-news-feeder && python main.py >> logs/news-feeder.log 2>&1
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- [News API](https://newsapi.org/) - 뉴스 데이터 제공
- [Google Gemini](https://ai.google.dev/) - AI 처리
- [Jinja2](https://jinja.palletsprojects.com/) - 템플릿 엔진
