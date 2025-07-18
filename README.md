# 🤖 AI 뉴스 피더 (AI News Feeder)

매일 아침, 지정한 이메일로 최신 AI 관련 뉴스를 요약하여 보내주는 자동화 프로젝트입니다. GitHub Actions를 이용하여 서버 없이 무료로 운영할 수 있습니다.

## ✨ 주요 기능

-   **자동 뉴스 수집**: News API를 통해 매일 새로운 AI 관련 뉴스를 가져옵니다.
-   **AI 기반 요약**: Google Gemini API를 활용하여 수집된 뉴스를 한국어로 간결하게 요약합니다.
-   **이메일 발송**: 요약된 뉴스들을 지정된 이메일 주소로 발송합니다.
-   **서버리스 운영**: GitHub Actions의 스케줄 기능을 통해 별도의 서버 없이 매일 정해진 시간에 자동으로 실행됩니다. (기본 설정: 매일 아침 8시 KST)

## ⚙️ 동작 원리

1.  **스케줄 실행**: GitHub Actions가 정해진 시간(`cron: '0 23 * * *'`)에 워크플로우를 실행합니다.
2.  **환경 설정**: 파이썬 실행 환경을 구성하고 `requirements.txt`에 명시된 라이브러리들을 설치합니다.
3.  **스크립트 실행**: `main.py` 스크립트가 실행됩니다.
    -   News API에서 'AI', 'Machine Learning' 등의 키워드로 최신 뉴스를 가져옵니다.
    -   가져온 각 뉴스의 내용을 Gemini API에 보내 한국어 요약을 요청합니다.
    -   요약된 내용들을 HTML 형식으로 구성하여 SMTP를 통해 이메일로 발송합니다.
4.  **비밀 정보 관리**: API 키, 이메일 정보 등 모든 민감한 정보는 GitHub 저장소의 'Secrets'에 안전하게 저장하여 사용합니다.

## 🚀 설정 방법

1.  **저장소 Fork 또는 복제**: 이 저장소를 자신의 GitHub 계정으로 Fork 하거나 코드를 복제하여 새로운 저장소를 만듭니다.

2.  **API 키 발급**:
    -   **News API Key**: [newsapi.org](https://newsapi.org)에 가입하여 API 키를 발급받습니다. (무료 플랜 가능)
    -   **Gemini API Key**: [Google AI for Developers](https://ai.google.dev/)에 방문하여 API 키를 발급받습니다.

3.  **이메일 앱 비밀번호 생성**:
    -   보안을 위해 실제 계정 비밀번호 대신 **앱 비밀번호** 사용을 강력히 권장합니다.
    -   [Gmail 앱 비밀번호 생성 가이드](https://support.google.com/accounts/answer/185833)
    -   [Naver 앱 비밀번호 생성 가이드](https://help.naver.com/service/5640_5642/19849/2-2.%20%EC%95%B1%20%EB%B9%84%EB%B0%80%EB%B2%88%ED%98%B8%EB%A5%BC%20%EC%84%A4%EC%A0%95%ED%95%B4%EC%9A%94.)

4.  **GitHub Secrets 설정**:
    -   코드를 업로드한 GitHub 저장소에서 **Settings > Secrets and variables > Actions** 메뉴로 이동합니다.
    -   **New repository secret** 버튼을 눌러 아래 목록의 이름과 값으로 Secret을 등록합니다.

| Secret 이름            | 설명                                       | 예시 값                  | 필수 여부 |
| ---------------------- | ------------------------------------------ | ------------------------ | --------- |
| `NEWS_API_KEY`         | News API에서 발급받은 키                     | `a1b2c3d4e5f67890...`    | **필수**  |
| `GEMINI_API_KEY`       | Gemini API에서 발급받은 키                   | `AIzaSyA...`             | **필수**  |
| `SMTP_HOST`            | 사용하시는 이메일 서비스의 SMTP 서버 주소    | `smtp.gmail.com`         | **필수**  |
| `SMTP_PORT`            | SMTP 포트 번호 (보통 587 또는 465)         | `587`                    | **필수**  |
| `SMTP_USER`            | 뉴스를 발송할 이메일 주소                    | `your-email@gmail.com`   | **필수**  |
| `SMTP_PASSWORD`        | 위 이메일의 **앱 비밀번호**                  | `abcd efgh ijkl mnop`    | **필수**  |
| `RECIPIENT_EMAIL`      | 뉴스를 수신할 이메일 주소                    | `recipient@example.com`  | **필수**  |
| `SENDER_NAME`          | 발신자 이름 (기본값: "AI 뉴스 알리미")     | `AI News`                | 선택 사항 |
| `NEWS_ARTICLE_COUNT`   | 요약할 뉴스 기사의 개수 (기본값: 5)          | `3`                      | 선택 사항 |

## ▶️ 실행하기

-   **자동 실행**: 모든 설정이 완료되면, `.github/workflows/main.yml`에 설정된 스케줄에 따라 워크플로우가 자동으로 실행됩니다.
-   **수동 실행**: 즉시 테스트해보고 싶다면, 저장소의 **Actions** 탭 > **AI News Feeder** 워크플로우 > **Run workflow** 버튼을 눌러 수동으로 실행할 수 있습니다.
