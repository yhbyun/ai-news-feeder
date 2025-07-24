from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
from ...models.article import Article
from ...utils.logger import get_logger

logger = get_logger(__name__)

class NewsSource(ABC):
    """뉴스 소스 추상 클래스"""

    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
        self.enabled = True

    @abstractmethod
    def fetch_news(self, keywords: List[str], date_from: str) -> List[Article]:
        """뉴스를 가져오는 메서드"""
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """소스 이름 반환"""
        pass

    def is_enabled(self) -> bool:
        """소스가 활성화되어 있는지 확인"""
        return self.enabled

    def set_enabled(self, enabled: bool) -> None:
        """소스 활성화/비활성화 설정"""
        self.enabled = enabled

    def get_weight(self) -> float:
        """소스 가중치 반환"""
        return self.weight

    def set_weight(self, weight: float) -> None:
        """소스 가중치 설정"""
        self.weight = weight