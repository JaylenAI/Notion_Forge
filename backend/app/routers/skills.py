"""커스텀 스킬 관리 API

유저가 자기만의 스킬을 생성/수정/삭제할 수 있는 엔드포인트.
커스텀 스킬은 custom_skills/ 디렉토리에 저장되며, 내장 스킬과 동일한 형식.
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.skills import (
    delete_custom_skill,
    get_custom_skill,
    list_skills,
    load_skill,
    save_custom_skill,
)

router = APIRouter(prefix="/api/skills", tags=["skills"])


class CustomSkillRequest(BaseModel):
    skill_id: str
    name: str
    description: str
    keywords: str = ""
    content: str  # Full SKILL.md content (or just the body; frontmatter will be auto-generated)


SKILL_TEMPLATE = """---
name: {skill_id}
description: {description}
keywords: {keywords}
---

# {name}

{content}
"""


@router.get("")
async def get_all_skills():
    """전체 스킬 목록 (내장 + 커스텀)"""
    return {"skills": list_skills()}


@router.get("/{skill_id}")
async def get_skill_detail(skill_id: str):
    """스킬 상세 조회 (SKILL.md 전체 내용)"""
    # 커스텀 스킬 먼저
    custom = get_custom_skill(skill_id)
    if custom:
        return {**custom, "is_custom": True}

    # 내장 스킬
    content = load_skill(skill_id)
    if content:
        return {"id": skill_id, "content": content, "is_custom": False}

    return {"error": f"Skill '{skill_id}' not found"}


@router.post("")
async def create_custom_skill(req: CustomSkillRequest):
    """커스텀 스킬 생성

    유저가 시스템 프롬프트처럼 자기만의 스킬을 정의.
    AI가 이 스킬을 참고하여 맞춤형 템플릿을 생성.

    Example:
    {
      "skill_id": "meeting",
      "name": "Meeting Notes",
      "description": "회의록 템플릿 생성 (안건, 결정사항, 액션아이템)",
      "keywords": "회의,미팅,회의록,안건,meeting,minutes",
      "content": "회의록 템플릿을 만듭니다.\\n\\n## Template Structure\\n- callout: 회의 정보\\n- database_ref: 회의 기록 DB\\n- toggle: 템플릿 사용법\\n\\n## Database Properties\\n- 회의 제목: title\\n- 날짜: date\\n- 참석자: multi_select\\n- 안건: rich_text\\n- 결정사항: rich_text\\n- 상태: status"
    }
    """
    # SKILL.md에 frontmatter가 없으면 자동 생성
    content = req.content
    if not content.strip().startswith("---"):
        content = SKILL_TEMPLATE.format(
            skill_id=req.skill_id,
            name=req.name,
            description=req.description,
            keywords=req.keywords,
            content=req.content,
        )

    save_custom_skill(req.skill_id, content)
    return {
        "success": True,
        "skill_id": req.skill_id,
        "message": f"커스텀 스킬 '{req.name}' 생성 완료! AI가 이제 이 스킬을 참고합니다.",
    }


@router.put("/{skill_id}")
async def update_custom_skill(skill_id: str, req: CustomSkillRequest):
    """커스텀 스킬 수정"""
    content = req.content
    if not content.strip().startswith("---"):
        content = SKILL_TEMPLATE.format(
            skill_id=skill_id,
            name=req.name,
            description=req.description,
            keywords=req.keywords,
            content=req.content,
        )
    save_custom_skill(skill_id, content)
    return {"success": True, "message": f"스킬 '{skill_id}' 업데이트 완료!"}


@router.delete("/{skill_id}")
async def remove_custom_skill(skill_id: str):
    """커스텀 스킬 삭제 (내장 스킬은 삭제 불가)"""
    if delete_custom_skill(skill_id):
        return {"success": True, "message": f"스킬 '{skill_id}' 삭제 완료"}
    return {"success": False, "message": f"커스텀 스킬 '{skill_id}'를 찾을 수 없습니다"}
