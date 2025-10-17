import requests
from datetime import datetime
from typing import List, Dict, Any
from ..models.article import Article
from ..config.settings import Settings
from ..utils.logger import get_logger
from ..utils.exceptions import NotificationError

logger = get_logger(__name__)

class TeamsService:
    """MS Teams 채널에 알림을 보내는 서비스 클래스"""

    def __init__(self, settings: Settings):
        self.webhook_url = settings.ms_teams_webhook_url

    def send_news_message(self, articles: List[Article], categories: List[Dict[str, Any]]) -> None:
        """뉴스 기사를 Adaptive Card 형식으로 만들어 Teams 채널에 보냅니다."""
        if not self.webhook_url:
            logger.warning("MS Teams 웹훅 URL이 설정되지 않아 메시지를 발송하지 않습니다.")
            return

        logger.info("MS Teams로 뉴스 메시지 발송을 시작합니다...")

        try:
            adaptive_card = self._create_adaptive_card(articles, categories)
            payload = {
                "type": "message",
                "attachments": [{
                    "contentType": "application/vnd.microsoft.card.adaptive",
                    "content": adaptive_card
                }]
            }

            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status() # 2xx 응답이 아니면 예외 발생

            logger.info("MS Teams 뉴스 메시지가 성공적으로 발송되었습니다.")

        except requests.exceptions.RequestException as e:
            logger.error(f"MS Teams 메시지 발송 중 네트워크 오류 발생: {e}")
            raise NotificationError(f"Teams 메시지 발송 실패: {e}")
        except Exception as e:
            logger.error(f"MS Teams 메시지 발송 중 예상치 못한 오류 발생: {e}")
            raise NotificationError(f"Teams 메시지 발송 실패: {e}")

    def _create_adaptive_card(self, articles: List[Article], categories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """뉴스 데이터로 Adaptive Card JSON을 생성합니다."""
        today_str = datetime.now().strftime('%Y년 %m월 %d일')
        title = f"🤖 오늘의 AI 뉴스 ({today_str})"

        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": title,
                    "size": "Large",
                    "weight": "Bolder"
                }
            ]
        }

        for category_info in categories:
            card["body"].append({
                "type": "TextBlock",
                "text": f"📌 {category_info['category_name']}",
                "size": "Medium",
                "weight": "Bolder",
                "color": "Good",
                "spacing": "Medium",
                "separator": True
            })

            for index in category_info['articles']:
                article = articles[index]

                # Adaptive Card의 각 기사 항목을 동적으로 구성
                items = [
                    {
                        "type": "TextBlock",
                        "text": f"[{article.korean_title}]({article.url})",
                        "weight": "Bolder",
                        "wrap": True
                    },
                    {
                        "type": "TextBlock",
                        "text": article.summary,
                        "wrap": True,
                        "spacing": "Small"
                    }
                ]

                if article.tags:
                    tags_text = ", ".join([f"`{tag}`" for tag in article.tags])
                    items.append({
                        "type": "TextBlock",
                        "text": tags_text,
                        "wrap": True,
                        "size": "Small",
                        "spacing": "Small",
                        "isSubtle": True
                    })

                items.append({
                    "type": "TextBlock",
                    "text": f"_{article.source_name}_",
                    "size": "Small",
                    "isSubtle": True,
                    "spacing": "Small"
                })

                article_block = {
                    "type": "Container",
                    "items": items
                }

                card["body"].append(article_block)

        return card
