"""ModifyClassifier: 수정 요청을 LLM으로 operation 분류 (Phase B1).

기존 regex 분류(modify_handler._classify_modify_type)의 경직성을 보완한다:
- "색 바꿔줘" 같은 요청이 regex엔 핸들러가 없어 도움말로 빠지던 문제
- 자유로운 발화("딜에 우선순위 좀 넣어줘")가 잘못 분류되던 문제

LLM이 현재 템플릿 맥락 + 요청을 보고 operation 하나를 고른다.
provider 실패/미설정/예산초과 시 None → 호출자가 regex로 폴백(robustness 유지).
"""

import logging
from typing import Any

logger = logging.getLogger("notionforge.modify_classifier")

# modify_handler._HANDLERS 키 + recolor
VALID_OPERATIONS = frozenset(
    {
        "recolor",
        "add_property",
        "delete_property",
        "add_view",
        "add_database",
        "add_relation",
        "add_formula",
        "add_sub_page",
        "add_block",
        "delete_item",
        "modify_default",
    }
)

CLASSIFY_PROMPT = """당신은 Notion 템플릿 수정 요청 분류기다. 사용자의 수정 요청을 아래 operation 중 정확히 하나로 분류하라.

현재 템플릿: {summary}

operation 목록:
- recolor: 색상/테마 변경 (예: "파란색으로 바꿔줘", "색 바꿔", "테마 초록으로")
- add_property: DB에 속성/필드 추가
- delete_property: 속성/필드 삭제·제거
- add_view: 뷰 추가/변경 (보드/캘린더/갤러리/타임라인/테이블/칸반)
- add_database: 새 데이터베이스 추가
- add_relation: 데이터베이스 간 연결(relation)
- add_formula: 수식/계산 속성 추가
- add_sub_page: 하위 페이지 추가
- add_block: 블록/섹션/내용/텍스트/FAQ 추가
- delete_item: 뷰 또는 블록 삭제
- modify_default: 위 어디에도 해당하지 않음

반드시 JSON만 출력: {{"operation": "<목록 중 하나>"}}"""


def _summary(result: dict[str, Any] | None, blueprint: dict[str, Any] | None) -> str:
    dbs = (result or {}).get("databases", []) or []
    names = [d.get("title", "?") for d in dbs]
    color = (blueprint or {}).get("metadata", {}).get("color_theme", "?")
    return f"DB {len(dbs)}개: {names}, 현재 색상: {color}"


async def classify_modification(
    message: str,
    result: dict[str, Any] | None = None,
    blueprint: dict[str, Any] | None = None,
    ai_key: str = "",
    ai_model: str = "",
    provider: Any = None,
) -> str | None:
    """수정 요청 → operation 이름. 실패/미설정 시 None(호출자가 regex 폴백)."""
    try:
        if provider is None:
            from app.agent.providers.router import ProviderRouter

            provider = ProviderRouter.resolve_with_fallback(api_key=ai_key, ai_model=ai_model)

        try:
            from app.core.cost_control import note_call

            note_call()
        except Exception:
            return None

        prompt = CLASSIFY_PROMPT.format(summary=_summary(result, blueprint))
        res = await provider.call_with_retry(prompt, message, model=ai_model, timeout=20.0)
        if isinstance(res, dict):
            op = res.get("operation")
            if op in VALID_OPERATIONS:
                logger.info(f"[ModifyClassifier] '{message[:30]}' → {op}")
                return op
        return None
    except Exception as e:
        logger.info(f"[ModifyClassifier 스킵] {str(e)[:80]}")
        return None
