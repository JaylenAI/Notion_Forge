"""사용자 의도 분석: Gemini (무료) / Claude (유료) / Mock 지원"""

import json
import logging
import re

from app.config import settings

logger = logging.getLogger("notionforge.intent_analyzer")
from app.schemas.blueprint import IntentResult

# 색상 매핑
COLOR_MAP: dict[str, str] = {
    "하늘색": "blue", "파란색": "blue", "블루": "blue", "blue": "blue",
    "주황색": "orange", "오렌지": "orange", "orange": "orange",
    "초록색": "green", "연두색": "green", "그린": "green", "green": "green",
    "빨간색": "red", "레드": "red", "코랄": "red", "red": "red",
    "보라색": "purple", "퍼플": "purple", "라벤더": "purple", "purple": "purple",
    "핑크": "pink", "분홍색": "pink", "pink": "pink",
    "노란색": "yellow", "옐로우": "yellow", "yellow": "yellow",
    "회색": "gray", "그레이": "gray", "모노": "gray", "gray": "gray",
}

TYPE_KEYWORDS: dict[str, list[str]] = {
    "dashboard": ["대시보드", "dashboard", "홈", "메인"],
    "tracker": ["트래커", "tracker", "습관", "목표", "루틴"],
    "bookmark": ["북마크", "bookmark", "즐겨찾기", "링크 정리", "사이트"],
    "project": ["프로젝트", "project", "칸반", "kanban", "스프린트"],
    "note": ["노트", "note", "수집", "일기", "시음", "독서", "기록"],
    "onboarding": ["온보딩", "인수인계", "신입", "가이드"],
    "crm": ["crm", "고객", "영업", "거래처"],
}

SYSTEM_PROMPT = """당신은 Notion 템플릿 생성 전문가입니다.
사용자의 자연어 요청을 분석하여 아래 JSON 형식으로만 응답하세요. JSON 외 다른 텍스트는 절대 포함하지 마세요.

{
  "intent": "CREATE",
  "template_type": "dashboard",
  "title": "프로젝트 대시보드",
  "color_theme": "orange",
  "sub_pages": [],
  "missing_info": [],
  "confidence": 0.9
}

intent 옵션: CREATE, MODIFY, QUESTION
template_type 옵션: dashboard, tracker, bookmark, project, note, onboarding, crm, custom
color_theme 옵션: blue, orange, green, red, purple, pink, yellow, gray, default

규칙:
- 한국어 색상을 영어로 매핑: "하늘색"→"blue", "주황색"→"orange", "초록색"→"green"
- 정보가 부족하면 confidence를 낮추고 missing_info에 질문 추가
- 반드시 유효한 JSON만 응답"""


async def analyze_intent(message: str) -> IntentResult:
    """사용자 메시지 의도 분석 (프로바이더 자동 선택)"""
    provider = settings.ai_provider

    if provider == "copilot":
        result = await _copilot_analyze(message)
    elif provider == "groq":
        result = await _groq_analyze(message)
    elif provider == "gemini":
        result = await _gemini_analyze(message)
    elif provider == "claude":
        result = await _claude_analyze(message)
    else:
        result = _mock_analyze(message)

    result.intent = _override_intent(message, result.intent)
    return result


async def _copilot_analyze(message: str) -> IntentResult:
    """GitHub Copilot SDK로 의도 분석. 실패 시 Mock 폴백."""
    try:
        from app.core.copilot_client import copilot_manager
        text = await copilot_manager.send(
            system_prompt=SYSTEM_PROMPT,
            user_message=message,
            model=settings.copilot_model,
        )
        if text:
            return _parse_ai_response(text)
    except Exception as e:
        logger.warning(f"[Copilot 의도분석 에러] {str(e)[:100]}")
    return _mock_analyze(message)


async def _groq_analyze(message: str) -> IntentResult:
    """Groq API (openai/gpt-oss-120b)로 의도 분석. 실패 시 Mock 폴백."""
    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.groq_api_key)
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message},
            ],
            temperature=0.3,
            max_tokens=1024,
        )

        text = response.choices[0].message.content or ""
        result = _parse_ai_response(text)
        if result.confidence > 0:
            return result
        return _mock_analyze(message)
    except Exception as e:
        logger.warning(f"[Groq 폴백] {e}")
        return _mock_analyze(message)


async def _gemini_analyze(message: str) -> IntentResult:
    """Gemini Flash API로 의도 분석 (무료). 실패 시 Mock 폴백."""
    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{SYSTEM_PROMPT}\n\n사용자 요청: {message}",
        )

        text = response.text or ""
        result = _parse_ai_response(text)
        if result.confidence > 0:
            return result
        return _mock_analyze(message)
    except Exception as e:
        logger.warning(f"[Gemini 폴백] {e}")
        return _mock_analyze(message)


async def _claude_analyze(message: str) -> IntentResult:
    """Claude API로 의도 분석 (유료)"""
    import anthropic

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
    response = await client.messages.create(
        model=settings.claude_model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": message}],
    )

    text = response.content[0].text
    return _parse_ai_response(text)


def _parse_ai_response(text: str) -> IntentResult:
    """AI 응답 텍스트에서 JSON 파싱"""
    json_match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
    if not json_match:
        return IntentResult(
            intent="QUESTION",
            template_type="custom",
            confidence=0.3,
            missing_info=["요청을 이해하지 못했습니다. 다시 설명해주세요."],
        )

    try:
        data = json.loads(json_match.group())
        filtered = {k: v for k, v in data.items() if k in IntentResult.model_fields and v is not None}
        result = IntentResult(**filtered)
        # 제목이 비어있으면 기본값
        if not result.title:
            type_names = {
                "dashboard": "대시보드", "tracker": "트래커", "bookmark": "북마크 사이트",
                "project": "프로젝트 보드", "note": "노트", "onboarding": "온보딩 가이드",
                "crm": "CRM", "custom": "My Workspace",
            }
            result.title = type_names.get(result.template_type, "My Workspace")
        return result
    except (json.JSONDecodeError, Exception):
        return _mock_analyze(json_match.group() if json_match else "")


def _override_intent(message: str, intent: str) -> str:
    """CREATE 키워드가 있으면 QUESTION을 CREATE로 강제 보정"""
    if intent == "QUESTION":
        msg = message.lower()
        create_keywords = ["만들어", "생성", "제작", "만들자", "ㄱㄱ", "구축", "설계"]
        if any(kw in msg for kw in create_keywords):
            return "CREATE"
    return intent


def _mock_analyze(message: str) -> IntentResult:
    """Mock 패턴 매칭으로 의도 분석"""
    msg = message.lower()

    if any(w in msg for w in ["가능", "할 수", "뭐야", "어때", "?"]):
        intent = "QUESTION"
    elif any(w in msg for w in ["만들어", "생성", "제작", "만들자", "ㄱㄱ"]):
        intent = "CREATE"
    elif any(w in msg for w in ["추가", "수정", "바꿔", "변경", "삭제", "없애", "제거", "연결", "넣어", "빼"]):
        intent = "MODIFY"
    else:
        intent = "CREATE"

    intent = _override_intent(message, intent)

    template_type = "custom"
    for t_type, keywords in TYPE_KEYWORDS.items():
        if any(k in msg for k in keywords):
            template_type = t_type
            break

    color_theme = "default"
    for kr, en in COLOR_MAP.items():
        if kr in msg:
            color_theme = en
            break

    title = {
        "dashboard": "대시보드", "tracker": "트래커", "bookmark": "북마크 사이트",
        "project": "프로젝트 보드", "note": "노트", "onboarding": "온보딩 가이드",
        "crm": "CRM", "custom": "My Workspace",
    }.get(template_type, "My Workspace")

    confidence = 0.9 if template_type != "custom" else 0.5

    sub_pages = _extract_sub_pages(message)
    missing_info = []
    if template_type == "custom":
        missing_info.append("어떤 용도의 템플릿인가요?")

    return IntentResult(
        intent=intent,
        template_type=template_type,
        title=title,
        color_theme=color_theme,
        sub_pages=sub_pages if sub_pages else None,
        missing_info=missing_info if missing_info else None,
        confidence=confidence,
    )


def _extract_sub_pages(message: str) -> list[str]:
    patterns = [
        r"하위\s*페이지\s*\d+개?\s*\(([^)]+)\)",
        r"하위\s*페이지[:\s]*([^.!]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, message)
        if match:
            raw = match.group(1)
            return [p.strip() for p in re.split(r"[,/、]", raw) if p.strip()]
    return []
