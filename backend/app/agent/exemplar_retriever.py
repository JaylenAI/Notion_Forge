"""ExemplarRetriever: 도메인 매칭 few-shot 예시 검색·주입 (Phase A5).

**벡터/임베딩 RAG가 아니다.** 기존 golden(레이아웃별 few-shot) 패턴을 확장해,
큐레이션된 고품질 recipe(멀티DB·relation·rollup, $50-99급)를 *예시 코퍼스*로 삼아
유저 요청 도메인에 맞는 것을 키워드/태그로 골라 생성 프롬프트에 "참고 우수 예시"로
주입한다. 목적: AI가 단일DB 대신 **연결된 멀티DB + 집계 구조를 모방**하게 만들어
단일DB가 $5-15에 머무는 핵심 약점(relation_rollup/linked_db)을 공략.

OSS·무DB 원칙 유지 — 새 의존성/벡터스토어 없음. router 패턴과 동일한 키워드 스코어링.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("notionforge.exemplar")

# recipes/ 디렉토리 (routers/recipes.py와 동일 규칙: backend/app/agent → parents[3] = repo root)
RECIPES_DIR = Path(__file__).resolve().parents[3] / "recipes"

_TAG_WEIGHT = 3
_NAME_WEIGHT = 2
_MIN_SCORE = 3  # 이 점수 미만이면 관련 예시 없음으로 간주(무관한 주입 방지)

# recipe 태그가 영어라 한국어 요청과 매칭되지 않던 문제(라이브에서 발견) 보완:
# recipe id별 한국어 도메인 키워드. 주 사용자가 한국어이므로 필수.
_KO_DOMAIN_HINTS: dict[str, tuple[str, ...]] = {
    "crm-dashboard": ("고객", "거래", "영업", "매출", "딜", "파이프라인", "세일즈", "계약"),
    "okr-dashboard": ("목표", "성과", "핵심결과", "지표", "분기목표"),
    "project-board": ("프로젝트", "작업", "태스크", "칸반", "일정관리", "업무"),
    "reading-log": ("독서", "도서", "읽은", "책"),
}


def _props(db: dict[str, Any]) -> dict[str, Any]:
    p = db.get("db_properties") or db.get("properties") or {}
    return p if isinstance(p, dict) else {}


def load_corpus() -> list[dict[str, Any]]:
    """recipe 코퍼스 로드 (blueprint를 가진 항목만)."""
    out: list[dict[str, Any]] = []
    if not RECIPES_DIR.exists():
        return out
    for f in sorted(RECIPES_DIR.glob("*.json")):
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(d, dict) and d.get("blueprint"):
                out.append(d)
        except Exception:
            continue
    return out


def _score(recipe: dict[str, Any], msg_lower: str) -> int:
    score = 0
    for tag in recipe.get("tags", []):
        if str(tag).lower() in msg_lower:
            score += _TAG_WEIGHT
    # 한국어 도메인 키워드 (영어 태그가 한국어 요청과 매칭 안 되는 문제 보완)
    for ko in _KO_DOMAIN_HINTS.get(recipe.get("id", ""), ()):
        if ko in msg_lower:
            score += _TAG_WEIGHT
    for field in ("name", "name_en"):
        for tok in str(recipe.get(field, "")).lower().split():
            if len(tok) >= 2 and tok in msg_lower:
                score += _NAME_WEIGHT
    return score


def retrieve_exemplars(user_message: str, k: int = 1) -> list[dict[str, Any]]:
    """요청과 키워드/태그가 겹치는 예시를 점수순으로 반환 (관련 없으면 빈 목록)."""
    msg = (user_message or "").lower()
    scored = [(r, _score(r, msg)) for r in load_corpus()]
    relevant = sorted([(r, s) for r, s in scored if s >= _MIN_SCORE], key=lambda x: x[1], reverse=True)
    return [r for r, _ in relevant[:k]]


def _summarize(recipe: dict[str, Any]) -> str:
    bp = recipe.get("blueprint", {})
    dbs = bp.get("databases", [])
    relations = rollups = formulas = 0
    titles = []
    for db in dbs:
        titles.append(db.get("title", "DB"))
        for spec in _props(db).values():
            t = spec if isinstance(spec, str) else (spec.get("type", "") if isinstance(spec, dict) else "")
            relations += t == "relation"
            rollups += t == "rollup"
            formulas += t == "formula"
    name = recipe.get("name", "예시")
    return (
        f"'{name}' — DB {len(dbs)}개({', '.join(titles)}), "
        f"relation {relations}·rollup {rollups}·formula {formulas}개로 연결된 구조."
    )


def build_exemplar_hint(user_message: str) -> str:
    """도메인 매칭 시 멀티DB 우수 예시의 구조 힌트를 생성(주입용). 없으면 빈 문자열.

    단일DB 예시는 '멀티DB 모방' 가치가 없으므로 주입하지 않는다(2개 이상일 때만).
    """
    for ex in retrieve_exemplars(user_message, k=1):
        bp = ex.get("blueprint", {})
        if len(bp.get("databases", [])) >= 2:
            return (
                "## 참고 우수 예시 (구조 모방)\n"
                f"{_summarize(ex)}\n"
                "요청 성격이 유사하면, 이처럼 **연결된 멀티 데이터베이스 + relation/rollup 집계** 구조로 "
                "설계하세요(단일 DB보다 실용적이고 완성도 높음). 단, 사용자가 '간단'을 명시하면 단순화하세요."
            )
    return ""
