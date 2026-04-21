"""Skill Matcher: 유저 메시지에서 최적 스킬을 매칭하고 가이드를 빌드

blueprint_generator.py에서 분리된 모듈.
"""

import logging

from app.skills import load_skill, _get_all_skills

logger = logging.getLogger("notionforge.skill_matcher")


TIER2_SKILLS = {
    "fitness", "habit", "health", "diet", "reading", "recipe", "movie", "music", "cafe",
    "project", "sprint", "bug", "meeting", "travel", "wedding", "goals",
    "bookmark", "inventory", "contact", "budget", "investment", "subscription",
    "study", "language", "sales",
    # Phase 4 추가
    "onboarding", "wiki", "sop", "team_home", "life_os",
    "diary", "gratitude", "review", "blog", "youtube", "social",
}


def _extract_skill_essentials(skill_md: str) -> str:
    """스킬 .md에서 핵심 패턴만 추출 (Required properties, Views, Block Order)"""
    lines = skill_md.split("\n")
    essentials: list[str] = []
    capture = False
    for line in lines:
        lower = line.lower().strip()
        # 핵심 섹션 캡처
        if any(kw in lower for kw in ["required properties", "### views", "### layout", "block order", "must-have"]):
            capture = True
        elif line.startswith("## ") and capture:
            capture = False
        if capture and line.strip():
            essentials.append(line)
        if len(essentials) > 12:
            break
    return "\n".join(essentials) if essentials else "\n".join(lines[4:12])


def _match_specific_skill(user_message: str) -> str | None:
    """유저 메시지에서 세분화 스킬(Tier 2)을 우선 매칭, 없으면 Tier 1"""
    msg = user_message.lower()
    all_skills = _get_all_skills()

    # Pass 1: 세분화 스킬(Tier 2) 먼저 검사 — 더 구체적
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

    if best_t2 and best_t2_score > 0:
        return best_t2

    # Pass 2: Tier 1 (범용 카테고리)
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

    return best_t1 if best_t1_score > 0 else None


def build_skill_guide(user_message: str = "") -> str:
    """유저 메시지에 맞는 최적 스킬을 우선 로딩, 나머지는 목록만 제공"""
    all_skills = _get_all_skills()

    # 1. 유저 메시지에 맞는 세분화 스킬 찾기
    matched_skill = _match_specific_skill(user_message) if user_message else None
    parts: list[str] = []

    if matched_skill:
        skill_md = load_skill(matched_skill)
        if skill_md:
            # 매칭된 스킬은 전체 내용을 로딩 (핵심 DB 구조 + 뷰 + 패턴)
            essentials = _extract_skill_essentials(skill_md)
            info = all_skills.get(matched_skill, {})
            parts.append(f"## MATCHED SKILL: {matched_skill} ({info.get('description', '')[:50]})\n{essentials}\n⚠️ FOLLOW THIS SKILL'S DB PROPERTIES AND VIEWS EXACTLY!")
            logger.info(f"[Skill Match] {matched_skill} (키워드 매칭)")

    # 2. 나머지 스킬은 이름+설명만 (토큰 절약)
    parts.append("## Available Skills (use matched skill above if available):")
    for skill_id, info in all_skills.items():
        if skill_id != matched_skill:
            parts.append(f"- {skill_id}: {info['description'][:50]}")

    return "\n".join(parts)
