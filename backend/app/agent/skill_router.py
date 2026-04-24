"""SkillRouter: 키워드 매칭 + LLM 분류 하이브리드 스킬 라우팅

빠른 경로(키워드 매칭 score ≥ 2)는 LLM 호출 없이 즉시 반환.
애매한 경우(score ≤ 1)에만 LLM으로 정밀 분류.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from app.skills import _get_all_skills, load_skill

logger = logging.getLogger("notionforge.skill_router")

TIER2_SKILLS = {
    "fitness", "habit", "health", "diet", "reading", "recipe", "movie", "music", "cafe",
    "project", "sprint", "bug", "meeting", "travel", "wedding", "goals",
    "bookmark", "inventory", "contact", "budget", "investment", "subscription",
    "study", "language", "sales",
    "onboarding", "wiki", "sop", "team_home", "life_os",
    "diary", "gratitude", "review", "blog", "youtube", "social",
}

CLASSIFY_SYSTEM = """You are a template skill classifier. Given a user request, pick the BEST matching skill_id.

Available skills:
{skill_list}

Output JSON only:
{{"skill_id": "...", "confidence": 0.0-1.0, "reasoning": "1문장"}}

Rules:
- Pick the most specific skill (Tier 2 over Tier 1)
- If no skill fits well, set confidence < 0.3
- Do NOT invent new skill IDs
"""


@dataclass(frozen=True)
class SkillMatch:
    skill_id: str | None
    confidence: float
    method: str


def _keyword_score(user_message: str) -> tuple[str | None, int, str | None, int]:
    """키워드 매칭 스코어 계산. (best_t2, t2_score, best_t1, t1_score) 반환."""
    msg = user_message.lower()
    all_skills = _get_all_skills()

    best_t2: str | None = None
    best_t2_score = 0
    for skill_id, info in all_skills.items():
        if skill_id not in TIER2_SKILLS:
            continue
        keywords = info.get("keywords", "").split(",")
        score = sum(1 for kw in keywords if kw.strip() and kw.strip() in msg)
        if score > best_t2_score:
            best_t2_score = score
            best_t2 = skill_id

    best_t1: str | None = None
    best_t1_score = 0
    for skill_id, info in all_skills.items():
        if skill_id in TIER2_SKILLS:
            continue
        keywords = info.get("keywords", "").split(",")
        score = sum(1 for kw in keywords if kw.strip() and kw.strip() in msg)
        if score > best_t1_score:
            best_t1_score = score
            best_t1 = skill_id

    return best_t2, best_t2_score, best_t1, best_t1_score


async def _llm_classify(user_message: str, provider: Any) -> SkillMatch:
    """LLM으로 스킬 분류"""
    all_skills = _get_all_skills()
    skill_list = "\n".join(f"- {sid}: {info['description'][:60]}" for sid, info in all_skills.items())
    system = CLASSIFY_SYSTEM.format(skill_list=skill_list)

    try:
        result = await provider.call(system, user_message)
        if result and isinstance(result, dict):
            skill_id = result.get("skill_id", "")
            confidence = float(result.get("confidence", 0))
            if skill_id in all_skills and confidence >= 0.3:
                logger.info(f"[SkillRouter/LLM] {skill_id} (conf={confidence:.2f})")
                return SkillMatch(skill_id=skill_id, confidence=confidence, method="llm")
    except Exception as e:
        logger.warning(f"[SkillRouter/LLM] 분류 실패: {e}")

    return SkillMatch(skill_id=None, confidence=0.0, method="llm_fallback")


async def route_skill(user_message: str, provider: Any = None) -> SkillMatch:
    """하이브리드 스킬 라우팅: 키워드 매칭(빠른 경로) + LLM 분류(정밀 경로)"""
    best_t2, t2_score, best_t1, t1_score = _keyword_score(user_message)

    if best_t2 and t2_score >= 2:
        logger.info(f"[SkillRouter/Keyword] {best_t2} (score={t2_score}, fast-path)")
        return SkillMatch(skill_id=best_t2, confidence=min(t2_score / 3, 1.0), method="keyword")

    if best_t1 and t1_score >= 2:
        logger.info(f"[SkillRouter/Keyword] {best_t1} (score={t1_score}, fast-path)")
        return SkillMatch(skill_id=best_t1, confidence=min(t1_score / 3, 1.0), method="keyword")

    if provider:
        llm_result = await _llm_classify(user_message, provider)
        if llm_result.skill_id:
            return llm_result

    if best_t2 and t2_score > 0:
        return SkillMatch(skill_id=best_t2, confidence=0.3, method="keyword_weak")
    if best_t1 and t1_score > 0:
        return SkillMatch(skill_id=best_t1, confidence=0.3, method="keyword_weak")

    return SkillMatch(skill_id=None, confidence=0.0, method="none")


def _extract_skill_essentials(skill_md: str) -> str:
    """스킬 .md에서 핵심 패턴만 추출"""
    lines = skill_md.split("\n")
    essentials: list[str] = []
    capture = False
    for line in lines:
        lower = line.lower().strip()
        if any(kw in lower for kw in ["required properties", "### views", "### layout", "block order", "must-have"]):
            capture = True
        elif line.startswith("## ") and capture:
            capture = False
        if capture and line.strip():
            essentials.append(line)
        if len(essentials) > 12:
            break
    return "\n".join(essentials) if essentials else "\n".join(lines[4:12])


async def build_skill_guide(user_message: str = "", provider: Any = None) -> tuple[str, SkillMatch]:
    """유저 메시지에 맞는 최적 스킬 가이드 빌드. (guide_text, match) 반환."""
    all_skills = _get_all_skills()
    match = await route_skill(user_message, provider=provider) if user_message else SkillMatch(None, 0.0, "none")

    parts: list[str] = []

    if match.skill_id:
        skill_md = load_skill(match.skill_id)
        if skill_md:
            essentials = _extract_skill_essentials(skill_md)
            info = all_skills.get(match.skill_id, {})
            parts.append(
                f"## MATCHED SKILL: {match.skill_id} ({info.get('description', '')[:50]})\n"
                f"Match: {match.method} (conf={match.confidence:.2f})\n"
                f"{essentials}\n"
                f"⚠️ FOLLOW THIS SKILL'S DB PROPERTIES AND VIEWS EXACTLY!"
            )
            logger.info(f"[SkillRouter] matched={match.skill_id}, method={match.method}, conf={match.confidence:.2f}")

    parts.append("## Available Skills (use matched skill above if available):")
    for skill_id, info in all_skills.items():
        if skill_id != match.skill_id:
            parts.append(f"- {skill_id}: {info['description'][:50]}")

    return "\n".join(parts), match
