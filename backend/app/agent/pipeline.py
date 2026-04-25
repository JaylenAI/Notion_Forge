"""멀티 에이전트 파이프라인: Architect → Designer → Content → Validator

각 에이전트가 전문 역할을 수행하여 더 높은 품질의 템플릿 생성:
1. Architect: 구조 설계 (DB 수, 속성, 관계, 서브페이지)
2. Designer: 비주얼 설계 (색상, 레이아웃, 블록 배치)
3. Content: 콘텐츠 생성 (샘플 데이터, 가이드, FAQ)
4. Validator: 검증 + 수정 (규칙 준수, 누락 체크)
"""

import json
from typing import Any, AsyncGenerator

ARCHITECT_PROMPT = """You are a Notion template ARCHITECT. Given a user request, design the STRUCTURE only.

Output JSON:
{{
  "title": "한국어 제목",
  "skill": "skill_name",
  "complexity": "simple|medium|complex",
  "databases": [
    {{
      "title": "DB명", "purpose": "용도 설명",
      "properties": {{"이름": "title", "상태": "status", ...}},
      "relations": [{{"target_db_index": 1, "property_name": "관련 DB"}}],
      "views": ["board", "calendar"]
    }}
  ],
  "sub_pages": [{{"name": "페이지명", "purpose": "용도"}}],
  "layout": "pattern_A|pattern_B|pattern_C|pattern_D"
}}

Rules:
- Simple: 1 DB, 0-1 sub_pages
- Medium: 1-2 DB, 2-3 sub_pages
- Complex: 3-4 DB, 5+ sub_pages with relations
- Always include title property in every DB
- Maximum 8 properties per DB
"""

DESIGNER_PROMPT = """You are a Notion template DESIGNER. Given an architecture, design the VISUAL layout.

Input: architecture JSON from Architect
Output: Add to the architecture:
{{
  "color": "primary_color",
  "cover_category": "category",
  "icon": "emoji",
  "blocks": [
    {{"type": "callout", "text": "...", "icon": "...", "color": "..._background"}},
    {{"type": "paragraph", "text": ""}},
    ...
  ]
}}

Design Rules:
- 2-3 color palette only
- Use column_list for dashboards (30/70 or 33/33/34)
- NEVER put database_ref inside column_list
- Empty paragraphs between sections
- Welcome callout at top, guide toggle at bottom
- Use rich_text array for mixed formatting in callouts
"""

CONTENT_PROMPT = """You are a Notion template CONTENT creator. Given a designed template, add rich content.

Add to each database:
- "sample_items": 5+ realistic Korean items with ALL properties filled
- "description": 1-sentence Korean description
- "icon": emoji for DB

Add to each sub_page:
- "blocks": [callout, heading, bulleted_list, toggle] with real content

Add to main:
- FAQ toggle with 2-3 real Q&A pairs
- Guide toggle with numbered_list steps

Rules:
- Status values: 시작 전, 진행 중, 완료
- Spread samples across all statuses
- Korean text only (unless [LANGUAGE] specified)
"""

VALIDATOR_PROMPT = """You are a Notion template VALIDATOR. Check the complete blueprint and fix issues.

Check these rules:
1. Every DB has a title property
2. database_ref NOT inside column_list
3. Maximum 3 colors used
4. Status values are: 시작 전, 진행 중, 완료
5. At least 5 sample items per DB
6. Welcome callout exists
7. Guide/FAQ toggle exists
8. Empty paragraphs between sections
9. Sub_pages have blocks (not empty)
10. cover_category matches template topic

Output the FIXED complete blueprint JSON.
If no fixes needed, output the same JSON unchanged.
"""


async def _call_agent(
    system_prompt: str, user_content: str, ai_key: str = "", ai_model: str = ""
) -> dict[str, Any] | None:
    """단일 에이전트 호출 — ProviderRouter 기반"""
    from app.agent.providers.router import ProviderRouter

    provider = ProviderRouter.resolve(api_key=ai_key, ai_model=ai_model)
    max_chars = provider.get_max_prompt_chars()
    prompt = system_prompt
    if max_chars > 0 and len(prompt) > max_chars:
        prompt = prompt[:max_chars]

    return await provider.call(prompt, user_content, model=ai_model)


async def multi_agent_pipeline(
    user_message: str,
    ai_key: str = "",
    ai_model: str = "",
) -> AsyncGenerator[dict[str, Any], None]:
    """4단계 멀티 에이전트 파이프라인 (스트리밍)"""

    # Stage 1: Architect
    yield {"stage": "architect", "message": "🏗️ Architect가 구조를 설계하고 있어요..."}
    architecture = await _call_agent(ARCHITECT_PROMPT, user_message, ai_key, ai_model)
    if not architecture:
        yield {"stage": "error", "message": "Architect 실패 — 단일 에이전트로 폴백"}
        return
    yield {"stage": "architect_done", "message": f"✅ 구조 설계 완료: DB {len(architecture.get('databases', []))}개"}

    # Stage 2: Designer
    yield {"stage": "designer", "message": "🎨 Designer가 비주얼을 설계하고 있어요..."}
    design_input = f"Architecture:\n{json.dumps(architecture, ensure_ascii=False)}\n\nOriginal request: {user_message}"
    design = await _call_agent(DESIGNER_PROMPT, design_input, ai_key, ai_model)
    if design:
        # Merge design into architecture
        architecture.update({k: v for k, v in design.items() if k in ("color", "cover_category", "icon", "blocks")})
    yield {"stage": "designer_done", "message": f"✅ 비주얼 설계 완료: {architecture.get('color', 'blue')} 테마"}

    # Stage 3: Content
    yield {"stage": "content", "message": "📝 Content가 콘텐츠를 생성하고 있어요..."}
    content_input = f"Template:\n{json.dumps(architecture, ensure_ascii=False)}\n\nOriginal request: {user_message}"
    content = await _call_agent(CONTENT_PROMPT, content_input, ai_key, ai_model)
    if content:
        # Merge content (sample_items, sub_page blocks, FAQ)
        if "databases" in content:
            for i, db in enumerate(content["databases"]):
                if i < len(architecture.get("databases", [])):
                    architecture["databases"][i].update(
                        {k: v for k, v in db.items() if k in ("sample_items", "description", "icon")}
                    )
        if "sub_pages" in content:
            architecture["sub_pages"] = content["sub_pages"]
        if "faq" in content:
            architecture["faq"] = content["faq"]
    yield {"stage": "content_done", "message": "✅ 콘텐츠 생성 완료"}

    # Stage 4: Validator
    yield {"stage": "validator", "message": "✅ Validator가 검증하고 있어요..."}
    validator_input = f"Blueprint to validate:\n{json.dumps(architecture, ensure_ascii=False)}"
    validated = await _call_agent(VALIDATOR_PROMPT, validator_input, ai_key, ai_model)
    if validated and (validated.get("databases") or validated.get("db_properties")):
        architecture = validated
    yield {"stage": "validator_done", "message": "✅ 검증 완료"}

    yield {"stage": "complete", "blueprint": architecture}
