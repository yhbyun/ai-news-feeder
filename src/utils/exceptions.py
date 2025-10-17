class NewsFetchError(Exception):
    """뉴스 수집 중 발생하는 오류"""
    pass

class AIProcessingError(Exception):
    """AI 처리 중 발생하는 오류"""
    pass

class NotificationError(Exception):
    """알림 발송 중 발생하는 최상위 오류"""
    pass

class EmailSendError(NotificationError):
    """이메일 발송 중 발생하는 오류"""
    pass

class ConfigurationError(Exception):
    """설정 관련 오류"""
    pass

class TemplateError(Exception):
    """템플릿 처리 중 발생하는 오류"""
    pass
