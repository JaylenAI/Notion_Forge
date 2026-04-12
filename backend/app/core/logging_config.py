"""Structured JSON Logging 설정

structlog 의존성 없이 Python 기본 logging + JSON 포맷터로 구현.
모든 notionforge.* 로거가 JSON 형식으로 출력.
"""

import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):
    """JSON 형식 로그 포맷터"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # 추가 필드 (extra에 넣은 key-value)
        for key in ("skill", "layout", "model", "duration_ms", "tokens",
                     "blocks", "databases", "attempt", "error", "stage",
                     "user_input_length", "risk_level"):
            val = getattr(record, key, None)
            if val is not None:
                log_entry[key] = val

        if record.exc_info and record.exc_info[1]:
            log_entry["exception"] = str(record.exc_info[1])

        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str = "INFO") -> None:
    """애플리케이션 로깅 초기화"""
    root_logger = logging.getLogger("notionforge")
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # 기존 핸들러 제거 (중복 방지)
    root_logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)

    # 라이브러리 로깅 레벨 조정
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("notion_client").setLevel(logging.WARNING)
