from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Article:
    """뉴스 기사를 나타내는 모델 클래스"""

    # 기본 필드
    title: str
    description: str
    url: str
    source_name: str
    source_id: str
    published_at: Optional[datetime] = None

    # AI 처리 후 필드
    korean_title: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = field(default_factory=list)

    # 품질 평가 필드
    quality_score: float = 0.0
    weight: float = 1.0

    def __post_init__(self):
        """데이터 검증 및 기본값 설정"""
        if not self.title:
            raise ValueError("제목은 필수입니다.")

        if not self.url:
            raise ValueError("URL은 필수입니다.")

        if not self.source_name:
            self.source_name = "Unknown"

    def to_dict(self) -> dict:
        """딕셔너리 형태로 변환"""
        return {
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'source_name': self.source_name,
            'source_id': self.source_id,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'korean_title': self.korean_title,
            'summary': self.summary,
            'tags': self.tags,
            'quality_score': self.quality_score,
            'weight': self.weight
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Article':
        """딕셔너리에서 Article 객체 생성"""
        published_at = None
        if data.get('published_at'):
            try:
                published_at = datetime.fromisoformat(data['published_at'])
            except ValueError:
                pass

        return cls(
            title=data.get('title', ''),
            description=data.get('description', ''),
            url=data.get('url', ''),
            source_name=data.get('source_name', 'Unknown'),
            source_id=data.get('source_id', ''),
            published_at=published_at,
            korean_title=data.get('korean_title'),
            summary=data.get('summary'),
            tags=data.get('tags', []),
            quality_score=data.get('quality_score', 0.0),
            weight=data.get('weight', 1.0)
        )