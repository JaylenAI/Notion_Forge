"""Input Guardrail: 사용자 입력 검증 + 프롬프트 인젝션 방어

검증 항목:
1. 메시지 길이 (2~2000자)
2. 빈 메시지 / 공백만 있는 메시지
3. 프롬프트 인젝션 패턴 탐지
4. 반복 문자 스팸 탐지
"""

import logging
import re
from dataclasses import dataclass

logger = logging.getLogger("notionforge.input_guardrail")

# 프롬프트 인젝션 패턴 (대소문자 무시)
_INJECTION_PATTERNS: list[re.Pattern] = [
    re.compile(r"ignore\s+(all\s+)?(previous|above|prior)\s+(instructions?|prompts?|rules?)", re.I),
    re.compile(r"disregard\s+(all\s+)?(previous|above|prior)", re.I),
    re.compile(r"forget\s+(all\s+)?(previous|above|prior|everything)", re.I),
    re.compile(r"you\s+are\s+now\s+(?:a|an|the)\s+", re.I),
    re.compile(r"act\s+as\s+(?:a|an|if)\s+", re.I),
    re.compile(r"pretend\s+(?:you|to\s+be)\s+", re.I),
    re.compile(r"system\s*:\s*", re.I),
    re.compile(r"\[SYSTEM\]", re.I),
    re.compile(r"<\s*(?:system|instruction|prompt)\s*>", re.I),
    re.compile(r"override\s+(?:your|all|the)\s+", re.I),
    re.compile(r"new\s+instructions?\s*:", re.I),
    re.compile(r"jailbreak", re.I),
    re.compile(r"do\s+anything\s+now", re.I),
    re.compile(r"DAN\s+mode", re.I),
]

MAX_REPEAT_RATIO = 0.7  # 단일 문자 70% 이상 반복 → 스팸


def _get_limits() -> tuple[int, int]:
    """설정에서 길이 제한 로드"""
    try:
        from app.config import settings

        return settings.input_min_length, settings.input_max_length
    except Exception:
        return 2, 2000


@dataclass
class GuardrailResult:
    """검증 결과"""

    is_valid: bool
    error_message: str = ""
    risk_level: str = "none"  # none, low, medium, high


def validate_input(message: str) -> GuardrailResult:
    """사용자 입력 메시지를 검증한다.

    Returns:
        GuardrailResult: is_valid=True이면 통과, False이면 차단
    """
    # 1. 빈 메시지
    stripped = message.strip()
    if not stripped:
        return GuardrailResult(
            is_valid=False,
            error_message="메시지를 입력해주세요.",
            risk_level="low",
        )

    # 2. 길이 검증
    min_len, max_len = _get_limits()
    if len(stripped) < min_len:
        return GuardrailResult(
            is_valid=False,
            error_message=f"메시지가 너무 짧습니다. (최소 {min_len}자)",
            risk_level="low",
        )

    if len(stripped) > max_len:
        return GuardrailResult(
            is_valid=False,
            error_message=f"메시지가 너무 깁니다. ({len(stripped)}자 / 최대 {max_len}자)",
            risk_level="low",
        )

    # 3. 반복 문자 스팸 탐지
    if len(stripped) >= 10:
        char_counts: dict[str, int] = {}
        for ch in stripped:
            if ch.strip():  # 공백 제외
                char_counts[ch] = char_counts.get(ch, 0) + 1
        non_space = sum(char_counts.values())
        if non_space > 0:
            max_char_count = max(char_counts.values())
            if max_char_count / non_space > MAX_REPEAT_RATIO:
                return GuardrailResult(
                    is_valid=False,
                    error_message="반복된 내용입니다. 구체적인 템플릿 요청을 입력해주세요.",
                    risk_level="medium",
                )

    # 4. 프롬프트 인젝션 탐지
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(stripped):
            logger.warning(f"[Guardrail] 프롬프트 인젝션 탐지: {stripped[:80]}...")
            return GuardrailResult(
                is_valid=False,
                error_message="요청을 처리할 수 없습니다. 템플릿 관련 요청을 입력해주세요.",
                risk_level="high",
            )

    return GuardrailResult(is_valid=True, risk_level="none")
