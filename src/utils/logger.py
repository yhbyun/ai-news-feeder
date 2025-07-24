import logging
from typing import Optional
import sys

def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """로거를 생성하고 반환합니다."""
    logger = logging.getLogger(name)

    # 이미 핸들러가 설정되어 있으면 기존 로거 반환
    if logger.handlers:
        return logger

    # 로그 레벨 설정
    if level is None:
        level = logging.INFO
    logger.setLevel(level)

    # 콘솔 핸들러 생성
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # 포맷터 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(console_handler)

    return logger