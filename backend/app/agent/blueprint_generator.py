"""AI 자유 설계 Blueprint Generator (dev-2 v3)

핵심 변경: AI가 blocks[] 배열도 직접 생성
- 하드코딩 빌더 함수 7개 제거
- AI가 유저 요청 복잡도에 따라 블록 수/구조를 자유롭게 결정
- 스킬 .md는 AI에게 규칙/가이드만 제공
"""

import json
import re
from typing import Any

from app.config import settings
from app.skills import load_skill, get_tool_enum_description, SKILL_REGISTRY

COVER_URLS: dict[str, str] = {
    # Gradient / Minimal
    "blue": "https://images.unsplash.com/photo-1557683316-973673baf926?w=1600",
    "orange": "https://images.unsplash.com/photo-1557682250-33bd709cbe85?w=1600",
    "green": "https://images.unsplash.com/photo-1557682224-5b8590cd9ec5?w=1600",
    "red": "https://images.unsplash.com/photo-1557682260-96773eb01377?w=1600",
    "purple": "https://images.unsplash.com/photo-1557682257-2f9c37a3a5f3?w=1600",
    "pink": "https://images.unsplash.com/photo-1557682268-e3955ed5d83f?w=1600",
    "yellow": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1600",
    "gray": "https://images.unsplash.com/photo-1553095066-5e3f2b0e6b2e?w=1600",
    "brown": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1600",
    "default": "https://images.unsplash.com/photo-1557683316-973673baf926?w=1600",
    # Category-specific covers
    "business": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1600",
    "finance": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1600",
    "fitness": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1600",
    "study": "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=1600",
    "travel": "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=1600",
    "food": "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1600",
    "creative": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1600",
    "nature": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1600",
    "tech": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=1600",
    "minimal": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1600",
}

# ============================================================
# 시스템 프롬프트: AI가 blocks[]도 직접 설계
# ============================================================

SYSTEM_PROMPT = """You are a WORLD-CLASS Notion template designer on the level of Thomas Frank, Easlo, and August Bradley.
Your templates must look like premium, $49+ templates sold on Gumroad — not amateur hobby pages.

## Available Skills: {skills}

## ═══════════════════════════════════════════
## PROFESSIONAL DESIGN PHILOSOPHY
## ═══════════════════════════════════════════

### 🎨 COLOR PALETTE RULE (MOST IMPORTANT)
- Pick EXACTLY 2-3 colors: ONE primary + ONE accent + gray for secondary text
- Apply the SAME primary color to: callout backgrounds, heading colors, select option colors, DB header
- NEVER use more than 3 colors. Consistency = professionalism
- Recommended palettes:
  * Business/Project: blue + gray (clean, professional)
  * Fitness/Health: orange + green (energetic, natural)
  * Finance: green + gray (money, trust)
  * Creative/Content: purple + pink (creative, vibrant)
  * Learning/Study: blue + purple (calm, intellectual)
  * Personal/Journal: pink + gray (gentle, reflective)
  * CRM/Sales: blue + orange (professional + urgency)

### 📐 LAYOUT HIERARCHY (What separates pro from amateur)
Every template MUST follow this visual hierarchy:
1. Welcome callout with icon — sets the tone, explains purpose (1-2 sentences)
2. Empty paragraph — BREATHING ROOM (critical for pro look)
3. column_list (30/70 split) — Left: quick stats/navigation, Right: main content
4. Primary database with multiple views
5. Empty paragraph — spacing
6. Secondary sections (toggles for guides, FAQ, tips)

### 🏗️ MANDATORY DASHBOARD COLUMN LAYOUT
For ANY template with a database, use column_list with 2 columns:
- LEFT column (30%): 2-3 callout blocks as "stat cards" or "quick links" (small, colored, with icon)
- RIGHT column (70%): heading + database_ref (main workspace)
This creates the "dashboard feel" that premium templates always have.

## ═══════════════════════════════════════════
## BLOCK TYPES & WHEN TO USE EACH
## ═══════════════════════════════════════════

### Available Block Types:
- callout: Welcome message, stat cards, tips, warnings. Use icon + color_background
- heading_1: Major sections (colored). Use sparingly (1-2 per page)
- heading_2: Sub-sections (colored or default)
- heading_3: Detail headers
- paragraph: Body text, descriptions. Use EMPTY paragraphs for whitespace
- divider: Section breaks. Use between major sections only (not everywhere)
- quote: Mission statements, key insights, motivational messages
- toggle: Usage guides, FAQ, expandable details. ALWAYS include at least 1 toggle with setup instructions
- to_do: Action items, onboarding checklists, daily tasks
- bulleted_list: Feature lists, categories, requirements
- numbered_list: Step-by-step processes, rankings
- column_list: Dashboard layouts (30/70), comparison layouts, stat sidebars
- database_ref: Inline database (db_index = 0,1,2... matching databases[] array)
- bookmark: External resource links
- table_of_contents: For complex templates (20+ blocks)
- code: Code snippets, formulas, technical reference

### DB Properties: title, rich_text, number, select, multi_select, status, date, checkbox, url, email
### DB Views: table, gallery, board, calendar, timeline, list
### Colors: default, gray, brown, orange, yellow, green, blue, purple, pink, red (add _background for blocks)

## ═══════════════════════════════════════════
## PROFESSIONAL TEMPLATE PATTERNS
## ═══════════════════════════════════════════

### Pattern A: Dashboard (most common, best for tracking/managing)
callout(welcome) → paragraph(empty) → column_list[
  column(30%): callout(stat1) + callout(stat2) + callout(quick-links),
  column(70%): heading_2(main section) + database_ref(0)
] → paragraph(empty) → divider → toggle(📖 사용 가이드) → toggle(❓ FAQ)

### Pattern B: Guided Setup (best for plans/guides)
callout(welcome) → paragraph(empty) → quote(mission/goal) → divider →
heading_1(section) → numbered_list(steps) → to_do(checklist) →
paragraph(empty) → heading_1(data) → database_ref(0) → divider →
toggle(tips) → toggle(FAQ)

### Pattern C: Multi-DB Hub (best for hub/CRM)
callout(welcome) → paragraph(empty) → column_list[
  column(30%): callout(nav-link1) + callout(nav-link2) + callout(nav-link3),
  column(70%): heading_2(primary) + database_ref(0)
] → paragraph(empty) → heading_1(secondary) → database_ref(1) →
paragraph(empty) → divider → toggle(guide) → toggle(FAQ)

### Pattern D: Collection/Gallery (best for collect/journal)
callout(welcome) → paragraph(empty) → heading_1(collection) →
paragraph(description) → database_ref(0) → paragraph(empty) →
column_list[
  column(50%): callout(stat) + bulleted_list(categories),
  column(50%): callout(stat) + bulleted_list(tags)
] → divider → toggle(guide)

## ═══════════════════════════════════════════
## BLOCK DIVERSITY RULES (CRITICAL!)
## ═══════════════════════════════════════════
You MUST use diverse blocks. Do NOT repeat the same callout→column→toggle pattern every time.

### MANDATORY BLOCK MIX:
- Every template MUST include at least 3 of these: quote, to_do, numbered_list, bulleted_list, bookmark
- Tracking templates: MUST include to_do (daily checklist) + quote (motivation)
- Management templates: MUST include numbered_list (workflow steps) + to_do (action items)
- Finance templates: MUST include bulleted_list (categories) + quote (financial goal)
- Collection templates: MUST include bulleted_list (categories) + bookmark (resources)
- Learning templates: MUST include numbered_list (study steps) + to_do (tasks) + bookmark (resources)
- CRM/Hub templates: MUST include sub_pages (2-3 linked pages) + multiple database_ref

### TOGGLE CONTENT RULES:
- Toggle "사용 가이드" MUST contain numbered_list with 3-5 setup steps, NOT just a paragraph
- Toggle "FAQ" MUST contain 2-3 real question/answer pairs
- Use toggle children_text for simple FAQs, use children array with numbered_list for guides

### TABLE_OF_CONTENTS RULE:
- Templates with 15+ blocks MUST include table_of_contents at the top (after welcome callout)

### SUB_PAGES RULE:
- Complex templates (hub, CRM, multi-DB) MUST include 2-3 sub_pages
- Each sub_page needs: name (Korean), icon (emoji), description (1 sentence)

### COVER_CATEGORY RULE:
- ALWAYS set cover_category matching the template topic:
  business, finance, fitness, study, travel, food, creative, nature, tech, minimal

### MULTI-DB RULE:
- Simple requests: 1 database
- Medium requests: 1-2 databases
- Complex requests (hub, CRM, startup): 2-3 databases with different purposes

## ═══════════════════════════════════════════
## ANTI-PATTERNS: NEVER DO THESE
## ═══════════════════════════════════════════
- NEVER use more than 3 colors (looks chaotic)
- NEVER skip whitespace paragraphs between sections (looks cramped)
- NEVER put more than 8 properties per database (overwhelming)
- NEVER create pages deeper than 2 levels (buried content)
- NEVER put everything on one flat list (use columns, toggles)
- NEVER mix random emoji styles (pick consistent icons)
- NEVER skip the welcome callout (every pro template has one)
- NEVER forget the usage guide toggle (users need instructions)
- NEVER leave sample data empty (minimum 5 realistic items per DB)
- NEVER use divider between every block (only between MAJOR sections)

## ═══════════════════════════════════════════
## DATABASE DESIGN RULES
## ═══════════════════════════════════════════
1. View-to-content matching is MANDATORY:
   - Has status/select property → MUST include board view
   - Has date property → MUST include calendar view
   - Has start+end dates → MUST include timeline view
   - Has image/visual content → MUST include gallery view
   - ALWAYS include table view as the "all data" fallback
2. Status property values MUST use these EXACT Korean names: "시작 전", "진행 중", "완료"
   - NEVER use "읽음", "읽는 중" etc. — ALWAYS map to 시작 전/진행 중/완료
3. Select options: use the PRIMARY color for most important option, gray for default
4. Sample items: minimum 5, ALL properties filled, realistic Korean data
5. Sample items must be spread across ALL statuses (not all in one state)
6. Properties limit: 5-8 per database (focused, not overwhelming)

## ═══════════════════════════════════════════
## OUTPUT FORMAT (JSON ONLY, NO OTHER TEXT)
## ═══════════════════════════════════════════
ALL text content MUST be in Korean.

{{
  "skill": "skill_name",
  "title": "한국어 제목",
  "icon": "emoji",
  "color": "primary_color_name",
  "cover_category": "category_for_cover_image",
  "blocks": [
    {{"type": "callout", "text": "환영 메시지", "icon": "emoji", "color": "color_background"}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "column_list", "columns": [
      [{{"type": "callout", "text": "📊 통계", "icon": "📊", "color": "blue_background"}}],
      [{{"type": "heading_2", "text": "메인 섹션"}}, {{"type": "database_ref", "db_index": 0}}]
    ]}},
    {{"type": "paragraph", "text": ""}},
    {{"type": "divider"}},
    {{"type": "toggle", "text": "📖 사용 가이드", "children_text": "사용법 설명"}}
  ],
  "databases": [
    {{
      "title": "DB명",
      "db_properties": {{"이름": "title", "상태": "status", "날짜": "date"}},
      "views": ["board", "calendar", "table"],
      "sample_items": [{{"이름": "항목1", "상태": "진행 중", "날짜": "2026-04-01", "icon": "🎯"}}]
    }}
  ],
  "sub_pages": [{{"name": "서브페이지명", "icon": "📁", "description": "설명"}}],
  "faq": [{{"q": "질문", "a": "답변"}}]
}}"""


# ============================================================
# 메인 함수
# ============================================================

def _detect_provider_from_key(api_key: str) -> str:
    if api_key.startswith("sk-ant-"):
        return "claude"
    if api_key.startswith("sk-"):
        return "openai"
    if api_key.startswith("gsk_"):
        return "groq"
    if api_key.startswith("AIza"):
        return "gemini"
    return ""


async def generate_blueprint(user_message: str, ai_key: str = "", ai_model: str = "") -> dict[str, Any]:
    """AI가 전체 구조를 자유롭게 설계. 실패 시 스마트 폴백."""
    # 스킬 가이드를 프롬프트에 주입
    skill_guide = ""
    # AI에게 스킬 목록 + 가이드 제공
    for skill_id in SKILL_REGISTRY:
        skill_md = load_skill(skill_id)
        if skill_md:
            # 스킬 .md에서 핵심 규칙만 추출 (너무 길면 잘림)
            lines = skill_md.split("\n")[:30]
            skill_guide += f"\n### {skill_id} skill guide:\n" + "\n".join(lines) + "\n"

    for attempt in range(2):
        try:
            ai_content = await _call_ai_for_content(user_message, ai_key=ai_key, ai_model=ai_model, extra_context=skill_guide)
            if ai_content and (ai_content.get("databases") or ai_content.get("db_properties")):
                blueprint = _assemble_blueprint(ai_content)
                blueprint["metadata"]["generation_method"] = "ai_dynamic"
                blueprint["metadata"]["skill_used"] = ai_content.get("skill", "custom")
                return blueprint
        except Exception as e:
            print(f"[AI Blueprint 시도 {attempt+1} 실패] {e}")

    print("[AI 실패 → 스마트 폴백 사용]")
    content = _smart_fallback(user_message)
    blueprint = _assemble_blueprint(content)
    blueprint["metadata"]["generation_method"] = "smart_fallback"
    return blueprint


# ============================================================
# AI 호출
# ============================================================

async def _call_ai_for_content(user_message: str, ai_key: str = "", ai_model: str = "", extra_context: str = "") -> dict[str, Any] | None:
    prompt = SYSTEM_PROMPT.format(skills=get_tool_enum_description())
    if extra_context:
        prompt += f"\n\n## Skill Guidelines:\n{extra_context[:2000]}"

    if ai_key:
        provider = _detect_provider_from_key(ai_key)
        if provider == "groq":
            return await _groq_call(prompt, user_message, api_key=ai_key, model=ai_model)
        elif provider == "gemini":
            return await _gemini_call(prompt, user_message, api_key=ai_key, model=ai_model)
        elif provider == "claude":
            return await _claude_call(prompt, user_message, api_key=ai_key, model=ai_model)
        elif provider == "openai":
            return await _openai_call(prompt, user_message, api_key=ai_key, model=ai_model)

    provider = settings.ai_provider
    if provider == "gemini":
        return await _gemini_call(prompt, user_message)
    elif provider == "groq":
        return await _groq_call(prompt, user_message)
    elif provider == "claude":
        return await _claude_call(prompt, user_message)
    else:
        return None


async def _groq_call(system: str, user_message: str, api_key: str = "", model: str = "") -> dict[str, Any] | None:
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=api_key or settings.groq_api_key)
        response = await client.chat.completions.create(
            model=model or "openai/gpt-oss-120b",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user_message}],
            temperature=0.3, max_tokens=4096,
        )
        return _parse_json_response(response.choices[0].message.content or "")
    except Exception as e:
        print(f"[Groq 에러] {e}")
        return None


async def _gemini_call(system: str, user_message: str, api_key: str = "", model: str = "") -> dict[str, Any] | None:
    try:
        from google import genai
        client = genai.Client(api_key=api_key or settings.gemini_api_key)
        response = await client.aio.models.generate_content(
            model=model or "gemini-2.5-flash",
            contents=f"{system}\n\nUser request: {user_message}",
        )
        return _parse_json_response(response.text or "")
    except Exception as e:
        print(f"[Gemini 에러] {e}")
        return None


async def _claude_call(system: str, user_message: str, api_key: str = "", model: str = "") -> dict[str, Any] | None:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=api_key or settings.anthropic_api_key)
        response = await client.messages.create(
            model=model or settings.claude_model, max_tokens=4096,
            system=system, messages=[{"role": "user", "content": user_message}],
        )
        return _parse_json_response(response.content[0].text)
    except Exception as e:
        print(f"[Claude 에러] {e}")
        return None


async def _openai_call(system: str, user_message: str, api_key: str = "", model: str = "") -> dict[str, Any] | None:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={"model": model or "gpt-4o-mini", "messages": [
                    {"role": "system", "content": system}, {"role": "user", "content": user_message}
                ], "temperature": 0.3, "max_tokens": 4096},
                timeout=30.0,
            )
            return _parse_json_response(resp.json()["choices"][0]["message"]["content"] or "")
    except Exception as e:
        print(f"[OpenAI 에러] {e}")
        return None


def _parse_json_response(text: str) -> dict[str, Any] | None:
    json_match = re.search(r"\{[\s\S]*\}", text)
    if not json_match:
        return None
    try:
        data = json.loads(json_match.group())
        if "databases" in data or "db_properties" in data:
            return data
        return None
    except (json.JSONDecodeError, Exception):
        return None


# ============================================================
# Blueprint 조립: AI가 준 데이터를 그대로 사용
# ============================================================

def _assemble_blueprint(content: dict) -> dict[str, Any]:
    """AI가 생성한 전체 구조를 Blueprint로 조립"""
    color = content.get("color", "gray")
    title = content.get("title", "My Template")

    # Pick cover: prefer category-specific, fallback to color-based
    cover_category = content.get("cover_category", "")
    cover_url = COVER_URLS.get(cover_category, COVER_URLS.get(color, COVER_URLS["default"]))

    blueprint: dict[str, Any] = {
        "version": "3.0",
        "metadata": {"title": title, "template_type": content.get("skill", "custom"), "color_theme": color},
        "main_page": {"title": title, "icon": content.get("icon", "📋"), "cover_url": cover_url},
        "blocks": [],
        "databases": [],
        "sub_pages": [],
    }

    # blocks: AI가 생성했으면 그대로, 없으면 기본 구조
    if content.get("blocks"):
        blueprint["blocks"] = content["blocks"]
    else:
        # blocks가 없으면 (폴백 등) 기본 구조 생성
        bg = f"{color}_background" if color != "default" else "default"
        blueprint["blocks"] = [
            {"type": "callout", "text": content.get("callout_text", f"{title}에 오신 걸 환영합니다!"), "icon": content.get("icon", "📋"), "color": bg},
            {"type": "divider"},
            {"type": "heading_1", "text": f"📊 {content.get('db_name', title)}", "color": bg},
            {"type": "database_ref", "db_index": 0},
            {"type": "divider"},
        ]
        for faq in content.get("faq", []):
            blueprint["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    # databases: AI 형식 통일
    if content.get("databases"):
        for db in content["databases"]:
            views = []
            for v in db.get("views", ["table"]):
                if isinstance(v, str):
                    views.append({"type": v, "title": v})
                elif isinstance(v, dict):
                    views.append(v)
            blueprint["databases"].append({
                "title": db.get("title", db.get("db_name", "Items")),
                "is_inline": True,
                "properties": db.get("db_properties", db.get("properties", {"이름": "title"})),
                "views": views,
                "sample_items": db.get("sample_items", []),
            })
    elif content.get("db_properties"):
        # 단일 DB (하위 호환)
        views = []
        for v in content.get("views", ["table"]):
            if isinstance(v, str):
                views.append({"type": v, "title": v})
            elif isinstance(v, dict):
                views.append(v)
        blueprint["databases"].append({
            "title": content.get("db_name", "Items"),
            "is_inline": True,
            "properties": content["db_properties"],
            "views": views,
            "sample_items": content.get("sample_items", []),
        })

    # sub_pages
    bg = f"{color}_background" if color != "default" else "default"
    for sub in content.get("sub_pages", []):
        blueprint["sub_pages"].append({
            "title": sub["name"], "icon": sub.get("icon", "📄"),
            "blocks": [
                {"type": "heading_1", "text": f"{sub.get('icon', '📄')} {sub['name']}", "color": bg},
                {"type": "callout", "text": sub.get("description", f"{sub['name']} 관련 내용을 정리하세요."), "icon": "📌", "color": bg},
                {"type": "divider"},
            ],
        })

    return blueprint


# ============================================================
# 스마트 폴백 (AI 실패 시)
# ============================================================

FALLBACK_TEMPLATES: dict[str, dict[str, Any]] = {
    "운동": {
        "skill": "track", "title": "운동 기록 일지", "icon": "🏋️", "color": "orange",
        "blocks": [
            {"type": "callout", "text": "매일 운동을 기록하고 건강한 습관을 만들어보세요! 💪", "icon": "🏋️", "color": "orange_background"},
            {"type": "divider"},
            {"type": "heading_1", "text": "🏋️ 운동 기록", "color": "orange_background"},
            {"type": "database_ref", "db_index": 0},
            {"type": "divider"},
            {"type": "toggle", "text": "💡 사용법", "children_text": "매일 아침 이 페이지를 열고 운동을 기록하세요. 캘린더 뷰에서 주간 패턴을 확인할 수 있습니다."},
        ],
        "databases": [{"title": "운동 기록", "db_properties": {
            "운동명": "title", "종류": {"type": "select", "options": [{"name": "유산소", "color": "blue"}, {"name": "근력", "color": "green"}, {"name": "스트레칭", "color": "purple"}]},
            "시간(분)": "number", "칼로리": "number", "날짜": "date", "완료": "checkbox",
        }, "views": ["calendar", "table"], "sample_items": [
            {"운동명": "아침 러닝 5km", "종류": "유산소", "시간(분)": 30, "칼로리": 300, "날짜": "2026-04-01", "완료": True, "icon": "🏃"},
            {"운동명": "스쿼트 4세트", "종류": "근력", "시간(분)": 40, "칼로리": 250, "날짜": "2026-04-02", "완료": False, "icon": "🏋️"},
            {"운동명": "요가 플로우", "종류": "스트레칭", "시간(분)": 50, "칼로리": 150, "날짜": "2026-04-03", "완료": True, "icon": "🧘"},
            {"운동명": "수영 1km", "종류": "유산소", "시간(분)": 45, "칼로리": 400, "날짜": "2026-04-04", "완료": False, "icon": "🏊"},
            {"운동명": "플랭크 3세트", "종류": "근력", "시간(분)": 15, "칼로리": 100, "날짜": "2026-04-05", "완료": True, "icon": "💪"},
        ]}],
        "sub_pages": [], "faq": [],
    },
    "독서": {
        "skill": "collect", "title": "독서 기록", "icon": "📚", "color": "green",
        "blocks": [
            {"type": "callout", "text": "읽은 책을 기록하고 나만의 서재를 만들어보세요! 📖", "icon": "📚", "color": "green_background"},
            {"type": "divider"},
            {"type": "heading_1", "text": "📚 독서 기록", "color": "green_background"},
            {"type": "database_ref", "db_index": 0},
            {"type": "divider"},
        ],
        "databases": [{"title": "독서 기록", "db_properties": {
            "책 제목": "title", "저자": "rich_text",
            "장르": {"type": "select", "options": [{"name": "소설", "color": "blue"}, {"name": "자기계발", "color": "green"}, {"name": "기술", "color": "orange"}, {"name": "에세이", "color": "purple"}]},
            "상태": "status", "평점": "number", "날짜": "date",
        }, "views": ["gallery", "table"], "sample_items": [
            {"책 제목": "원씽", "저자": "게리 켈러", "장르": "자기계발", "평점": 4, "날짜": "2026-03-15", "icon": "📕"},
            {"책 제목": "클린 코드", "저자": "로버트 마틴", "장르": "기술", "평점": 5, "날짜": "2026-03-20", "icon": "📘"},
            {"책 제목": "데미안", "저자": "헤르만 헤세", "장르": "소설", "평점": 4, "날짜": "2026-03-25", "icon": "📗"},
            {"책 제목": "아토믹 해빗", "저자": "제임스 클리어", "장르": "자기계발", "평점": 5, "날짜": "2026-03-28", "icon": "📙"},
            {"책 제목": "나는 나로 살기로 했다", "저자": "김수현", "장르": "에세이", "평점": 3, "날짜": "2026-04-01", "icon": "📔"},
        ]}],
        "sub_pages": [{"name": "읽고 싶은 책", "icon": "📚", "description": "읽을 책 목록"}], "faq": [],
    },
    "프로젝트": {
        "skill": "manage", "title": "프로젝트 보드", "icon": "📊", "color": "blue",
        "blocks": [
            {"type": "callout", "text": "프로젝트 진행 현황을 한눈에 관리하세요! 🗂️", "icon": "📊", "color": "blue_background"},
            {"type": "divider"},
            {"type": "heading_1", "text": "🗂️ 프로젝트 태스크", "color": "blue_background"},
            {"type": "database_ref", "db_index": 0},
            {"type": "divider"},
            {"type": "toggle", "text": "💡 사용법", "children_text": "보드 뷰에서 칸반으로, 타임라인 뷰에서 일정을 관리하세요."},
        ],
        "databases": [{"title": "프로젝트 태스크", "db_properties": {
            "태스크": "title", "상태": "status", "담당자": "rich_text",
            "우선순위": {"type": "select", "options": [{"name": "높음", "color": "red"}, {"name": "중간", "color": "yellow"}, {"name": "낮음", "color": "green"}]},
            "기한": "date", "카테고리": {"type": "select", "options": [{"name": "기획", "color": "blue"}, {"name": "개발", "color": "green"}, {"name": "디자인", "color": "purple"}, {"name": "QA", "color": "orange"}]},
        }, "views": ["board", "timeline", "table"], "sample_items": [
            {"태스크": "기획서 작성", "담당자": "김팀장", "우선순위": "높음", "기한": "2026-04-05", "카테고리": "기획", "icon": "📝"},
            {"태스크": "UI 디자인", "담당자": "이디자이너", "우선순위": "높음", "기한": "2026-04-10", "카테고리": "디자인", "icon": "🎨"},
            {"태스크": "백엔드 API", "담당자": "박개발", "우선순위": "중간", "기한": "2026-04-15", "카테고리": "개발", "icon": "⚙️"},
            {"태스크": "프론트엔드 구현", "담당자": "최개발", "우선순위": "중간", "기한": "2026-04-18", "카테고리": "개발", "icon": "🖥️"},
            {"태스크": "QA 테스트", "담당자": "정QA", "우선순위": "낮음", "기한": "2026-04-22", "카테고리": "QA", "icon": "🧪"},
        ]}],
        "sub_pages": [], "faq": [],
    },
}

FALLBACK_TEMPLATES["가계부"] = {
    "skill": "finance", "title": "가계부", "icon": "💰", "color": "green",
    "blocks": [
        {"type": "callout", "text": "수입과 지출을 체계적으로 기록하고 재정 목표를 달성하세요! 💰", "icon": "💰", "color": "green_background"},
        {"type": "divider"},
        {"type": "heading_1", "text": "💰 수입/지출 기록", "color": "green_background"},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
        {"type": "toggle", "text": "💡 사용법", "children_text": "매일 지출을 기록하세요. 카테고리별로 필터링하면 어디서 돈이 빠져나가는지 한눈에 볼 수 있습니다."},
    ],
    "databases": [{"title": "가계부", "db_properties": {
        "내역": "title", "금액": "number",
        "구분": {"type": "select", "options": [{"name": "수입", "color": "green"}, {"name": "지출", "color": "red"}, {"name": "저축", "color": "blue"}]},
        "카테고리": {"type": "select", "options": [{"name": "식비", "color": "orange"}, {"name": "교통", "color": "blue"}, {"name": "문화", "color": "purple"}, {"name": "생활", "color": "gray"}, {"name": "급여", "color": "green"}]},
        "날짜": "date", "메모": "rich_text",
    }, "views": ["table", "calendar"], "sample_items": [
        {"내역": "카페라떼", "금액": 5800, "구분": "지출", "카테고리": "식비", "날짜": "2026-04-01", "메모": "스타벅스", "icon": "☕"},
        {"내역": "월급", "금액": 3500000, "구분": "수입", "카테고리": "급여", "날짜": "2026-04-01", "메모": "4월 급여", "icon": "💵"},
        {"내역": "지하철 정기권", "금액": 55000, "구분": "지출", "카테고리": "교통", "날짜": "2026-04-02", "메모": "1개월", "icon": "🚇"},
        {"내역": "넷플릭스", "금액": 17000, "구분": "지출", "카테고리": "문화", "날짜": "2026-04-03", "메모": "월 구독", "icon": "🎬"},
        {"내역": "비상금 저축", "금액": 500000, "구분": "저축", "카테고리": "생활", "날짜": "2026-04-05", "메모": "CMA 계좌", "icon": "🏦"},
    ]}],
    "sub_pages": [{"name": "월별 정산", "icon": "📊", "description": "월별 수입/지출 정리"}], "faq": [],
}

FALLBACK_TEMPLATES["일기"] = {
    "skill": "journal", "title": "일기장", "icon": "📔", "color": "purple",
    "blocks": [
        {"type": "callout", "text": "오늘 하루를 기록하고 나를 돌아보는 시간을 가져보세요 ✨", "icon": "📔", "color": "purple_background"},
        {"type": "quote", "text": "기록하지 않으면 기억나지 않는다."},
        {"type": "divider"},
        {"type": "heading_1", "text": "📔 나의 일기", "color": "purple_background"},
        {"type": "database_ref", "db_index": 0},
    ],
    "databases": [{"title": "일기", "db_properties": {
        "제목": "title", "날짜": "date",
        "기분": {"type": "select", "options": [{"name": "최고", "color": "green"}, {"name": "좋음", "color": "blue"}, {"name": "보통", "color": "yellow"}, {"name": "우울", "color": "gray"}, {"name": "화남", "color": "red"}]},
        "내용": "rich_text", "에너지": "number", "하이라이트": "checkbox",
    }, "views": ["gallery", "calendar"], "sample_items": [
        {"제목": "봄바람이 부는 날", "날짜": "2026-04-01", "기분": "최고", "내용": "점심에 산책했다. 벚꽃이 예뻤다.", "에너지": 9, "하이라이트": True, "icon": "🌸"},
        {"제목": "코딩 마라톤", "날짜": "2026-04-02", "기분": "좋음", "내용": "새 프로젝트 시작. 집중이 잘 됐다.", "에너지": 7, "하이라이트": False, "icon": "💻"},
        {"제목": "비 오는 오후", "날짜": "2026-04-03", "기분": "보통", "내용": "하루종일 비가 왔다. 집에서 영화 봤다.", "에너지": 5, "하이라이트": False, "icon": "🌧️"},
        {"제목": "친구와 저녁", "날짜": "2026-04-04", "기분": "최고", "내용": "오랜만에 친구 만나서 맛있는 거 먹었다.", "에너지": 8, "하이라이트": True, "icon": "🍽️"},
        {"제목": "월요일 출근", "날짜": "2026-04-05", "기분": "보통", "내용": "주말이 너무 빨리 끝났다.", "에너지": 4, "하이라이트": False, "icon": "😴"},
    ]}],
    "sub_pages": [{"name": "감사 목록", "icon": "🙏", "description": "매일 감사한 것 3가지"}], "faq": [],
}

FALLBACK_TEMPLATES["콘텐츠"] = {
    "skill": "content", "title": "콘텐츠 캘린더", "icon": "📱", "color": "blue",
    "blocks": [
        {"type": "callout", "text": "콘텐츠 제작부터 발행까지 체계적으로 관리하세요! 📱", "icon": "📱", "color": "blue_background"},
        {"type": "divider"},
        {"type": "heading_1", "text": "📱 콘텐츠 파이프라인", "color": "blue_background"},
        {"type": "database_ref", "db_index": 0},
    ],
    "databases": [{"title": "콘텐츠", "db_properties": {
        "제목": "title", "상태": "status", "발행일": "date",
        "플랫폼": {"type": "select", "options": [{"name": "블로그", "color": "blue"}, {"name": "인스타", "color": "pink"}, {"name": "유튜브", "color": "red"}, {"name": "뉴스레터", "color": "green"}]},
        "형태": {"type": "select", "options": [{"name": "글", "color": "gray"}, {"name": "영상", "color": "orange"}, {"name": "이미지", "color": "purple"}]},
        "설명": "rich_text",
    }, "views": ["board", "calendar"], "sample_items": [
        {"제목": "AI 도구 비교 리뷰", "발행일": "2026-04-07", "플랫폼": "블로그", "형태": "글", "설명": "ChatGPT vs Claude 비교", "icon": "📝"},
        {"제목": "일상 브이로그", "발행일": "2026-04-10", "플랫폼": "유튜브", "형태": "영상", "설명": "주말 일상 촬영", "icon": "🎬"},
        {"제목": "디자인 팁 카드뉴스", "발행일": "2026-04-12", "플랫폼": "인스타", "형태": "이미지", "설명": "피그마 단축키 모음", "icon": "🎨"},
        {"제목": "주간 뉴스레터 #12", "발행일": "2026-04-14", "플랫폼": "뉴스레터", "형태": "글", "설명": "이번 주 테크 뉴스", "icon": "📬"},
        {"제목": "코딩 튜토리얼", "발행일": "2026-04-15", "플랫폼": "유튜브", "형태": "영상", "설명": "React 19 새 기능", "icon": "💻"},
    ]}],
    "sub_pages": [{"name": "아이디어 뱅크", "icon": "💡", "description": "콘텐츠 아이디어 모음"}], "faq": [],
}

FALLBACK_KEYWORDS: dict[str, list[str]] = {
    "운동": ["운동", "헬스", "피트니스", "트레이닝", "러닝", "조깅", "웨이트", "요가", "수영", "체중", "workout", "exercise", "fitness", "gym", "health"],
    "독서": ["독서", "책", "도서", "읽기", "서평", "북리뷰", "도서관", "book", "reading", "library"],
    "가계부": ["가계부", "예산", "지출", "수입", "돈", "재정", "구독", "절약", "저축", "투자", "재테크", "금융", "카드", "budget", "expense", "finance", "money", "subscription"],
    "일기": ["일기", "다이어리", "회고", "감사", "무드", "기분", "하루", "일상", "성찰", "journal", "diary", "mood", "gratitude", "reflection"],
    "콘텐츠": ["콘텐츠", "블로그", "유튜브", "인스타", "SNS", "소셜", "마케팅", "뉴스레터", "포스팅", "content", "blog", "youtube", "instagram", "social media", "newsletter"],
    "프로젝트": ["프로젝트", "태스크", "칸반", "스프린트", "업무", "보드", "일정", "스케줄", "캘린더", "계획", "준비", "여행", "결혼", "대시보드", "홈", "메인", "팀", "워크스페이스", "project", "task", "kanban", "sprint", "dashboard", "schedule", "plan", "travel", "crm", "고객", "영업", "리드"],
}


def _smart_fallback(user_message: str) -> dict[str, Any]:
    msg = user_message.lower()
    for template_key, keywords in FALLBACK_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            template = json.loads(json.dumps(FALLBACK_TEMPLATES[template_key]))
            clean_title = user_message.replace("만들어줘", "").replace("제작해줘", "").replace("!", "").strip()
            if clean_title and len(clean_title) < 30:
                template["title"] = clean_title
            return template

    # 기본 폴백
    defaults = json.loads(json.dumps(FALLBACK_TEMPLATES["프로젝트"]))
    clean_title = user_message.replace("만들어줘", "").replace("제작해줘", "").replace("!", "").strip()
    if clean_title and len(clean_title) < 30:
        defaults["title"] = clean_title
    return defaults
