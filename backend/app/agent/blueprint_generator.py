"""AI Tool Calling 기반 Blueprint Generator (dev-2)

흐름:
1. AI 1회 호출 → 스킬 선택 + 맥락 맞춤 내용 생성
2. 선택된 스킬 .md 로드 → 구조 가이드
3. 스킬 구조 + AI 내용 → Blueprint JSON 조립
4. 기존 Orchestrator가 실행 (변경 없음)
"""

import json
import re
from typing import Any

from app.config import settings
from app.skills import load_skill, get_tool_enum_description, SKILL_REGISTRY

COVER_URLS: dict[str, str] = {
    "blue": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200",
    "orange": "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=1200",
    "green": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200",
    "red": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1200",
    "purple": "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1200",
    "pink": "https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=1200",
    "yellow": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200",
    "gray": "https://images.unsplash.com/photo-1553095066-5e3f2b0e6b2e?w=1200",
    "default": "https://images.unsplash.com/photo-1557683316-973673baf926?w=1200",
}

SYSTEM_PROMPT = """You are a Notion template AI Agent.
Analyze the user's request and generate a template specification.

Select the most appropriate skill and create context-specific content.

Available skills:
{skills}

IMPORTANT RULES:
- Generate 5 realistic sample items with icons (NOT generic/placeholder data)
- DB properties should match the user's specific context
- Select options should have appropriate colors
- Views should match the use case (calendar for dates, board for status, gallery for collections)
- All text content (title, callout, samples) should be in Korean unless the context is English

CRITICAL SAMPLE DATA RULES:
- Every sample_item MUST include values for ALL db_properties (not just title and icon)
- For date properties: use real dates like "2026-04-01", "2026-04-03", etc.
- For status properties: spread across all statuses (not all "시작 전")
- For select properties: use different options across items
- For number properties: use realistic varied numbers
- For checkbox: mix true and false
- Calendar views REQUIRE date values in samples
- Board views REQUIRE status values in samples
- Gallery views REQUIRE icons in samples

BAD example (missing values):
  [{{"이름": "항목1", "icon": "📌"}}, {{"이름": "항목2", "icon": "📌"}}]

GOOD example (all values filled):
  [
    {{"운동명": "러닝 30분", "종류": "유산소", "시간": 30, "칼로리": 300, "날짜": "2026-04-01", "완료": true, "icon": "🏃"}},
    {{"운동명": "스쿼트 5세트", "종류": "근력", "시간": 40, "칼로리": 250, "날짜": "2026-04-02", "완료": false, "icon": "🏋️"}}
  ]

Respond with ONLY valid JSON, no other text:
{{
  "skill": "skill_name",
  "title": "template title",
  "icon": "emoji",
  "color": "blue|orange|green|red|purple|pink|yellow|gray",
  "callout_text": "welcome/guide message",
  "db_name": "database name",
  "db_properties": {{
    "property_name": "type_string" or {{"type": "select", "options": [{{"name": "opt", "color": "blue"}}]}}
  }},
  "views": ["gallery", "calendar", "board", "timeline", "table"],
  "sample_items": [
    {{"property_name": "value", "icon": "emoji"}},
  ],
  "sub_pages": [
    {{"name": "page name", "icon": "emoji", "description": "brief desc"}}
  ],
  "faq": [
    {{"q": "question", "a": "answer"}}
  ]
}}"""


async def generate_blueprint(user_message: str) -> dict[str, Any]:
    """AI Tool Calling으로 Blueprint 생성"""
    try:
        ai_content = await _call_ai_for_content(user_message)
        if ai_content:
            skill_name = ai_content.get("skill", "track")
            skill_md = load_skill(skill_name)
            blueprint = _assemble_blueprint(ai_content, skill_md)
            blueprint["metadata"]["generation_method"] = "ai_dynamic"
            blueprint["metadata"]["skill_used"] = skill_name
            return blueprint
    except Exception as e:
        print(f"[AI Blueprint 실패, 폴백 사용] {e}")

    # 폴백: Mock 분석으로 기본 템플릿
    return _fallback_blueprint(user_message)


async def _call_ai_for_content(user_message: str) -> dict[str, Any] | None:
    """AI 호출 → 스킬 선택 + 맥락 맞춤 내용 생성"""
    provider = settings.ai_provider

    prompt = SYSTEM_PROMPT.format(skills=get_tool_enum_description())

    if provider == "groq":
        return await _groq_call(prompt, user_message)
    elif provider == "gemini":
        return await _gemini_call(prompt, user_message)
    elif provider == "claude":
        return await _claude_call(prompt, user_message)
    else:
        return _mock_call(user_message)


async def _groq_call(system: str, user_message: str) -> dict[str, Any] | None:
    """Groq API 호출"""
    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=settings.groq_api_key)
        response = await client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        text = response.choices[0].message.content or ""
        return _parse_json_response(text)
    except Exception as e:
        print(f"[Groq 에러] {e}")
        return None


async def _gemini_call(system: str, user_message: str) -> dict[str, Any] | None:
    """Gemini API 호출"""
    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system}\n\nUser request: {user_message}",
        )
        text = response.text or ""
        return _parse_json_response(text)
    except Exception as e:
        print(f"[Gemini 에러] {e}")
        return None


async def _claude_call(system: str, user_message: str) -> dict[str, Any] | None:
    """Claude API 호출"""
    try:
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        text = response.content[0].text
        return _parse_json_response(text)
    except Exception as e:
        print(f"[Claude 에러] {e}")
        return None


def _mock_call(user_message: str) -> dict[str, Any]:
    """Mock 모드 (API 키 없을 때)"""
    msg = user_message.lower()

    # 스킬 선택 (키워드 매칭)
    skill = "track"
    for skill_id, info in SKILL_REGISTRY.items():
        keywords = info["keywords"].split(",")
        if any(kw.strip() in msg for kw in keywords):
            skill = skill_id
            break

    # 색상 감지
    color = "gray"
    color_map = {"파란": "blue", "하늘": "blue", "주황": "orange", "초록": "green",
                 "빨간": "red", "보라": "purple", "핑크": "pink", "노란": "yellow"}
    for kr, en in color_map.items():
        if kr in msg:
            color = en
            break

    return {
        "skill": skill,
        "title": user_message.replace("만들어줘", "").replace("만들어", "").strip() or "My Template",
        "icon": "📋",
        "color": color,
        "callout_text": "템플릿이 생성되었습니다. 자유롭게 수정해서 사용하세요!",
        "db_name": "Items",
        "db_properties": {"이름": "title", "상태": "status", "날짜": "date"},
        "views": ["table"],
        "sample_items": [
            {"이름": "항목 1", "icon": "📌"},
            {"이름": "항목 2", "icon": "📌"},
            {"이름": "항목 3", "icon": "📌"},
        ],
        "sub_pages": [],
        "faq": [],
    }


def _parse_json_response(text: str) -> dict[str, Any] | None:
    """AI 응답에서 JSON 파싱"""
    # JSON 블록 추출
    json_match = re.search(r"\{[\s\S]*\}", text)
    if not json_match:
        return None
    try:
        data = json.loads(json_match.group())
        # 필수 필드 확인
        if "skill" in data and "db_properties" in data:
            return data
        return None
    except (json.JSONDecodeError, Exception):
        return None


# ============================================================
# Blueprint 조립: 스킬 구조 + AI 내용 → Blueprint JSON
# ============================================================

def _assemble_blueprint(content: dict, skill_md: str | None) -> dict[str, Any]:
    """스킬 구조 + AI 내용 → Orchestrator가 실행할 수 있는 Blueprint"""
    skill = content.get("skill", "track")
    color = content.get("color", "gray")
    bg = f"{color}_background" if color != "default" else "default"
    title = content.get("title", "My Template")

    blueprint: dict[str, Any] = {
        "version": "2.0",
        "metadata": {
            "title": title,
            "template_type": skill,
            "color_theme": color,
        },
        "main_page": {
            "title": title,
            "icon": content.get("icon", "📋"),
            "cover_url": COVER_URLS.get(color, COVER_URLS["default"]),
        },
        "blocks": [],
        "databases": [],
        "sub_pages": [],
    }

    # 스킬별 구조 빌더
    builder = SKILL_BUILDERS.get(skill, _build_track)
    builder(blueprint, content, bg)

    return blueprint


def _build_track(bp: dict, c: dict, bg: str) -> None:
    """Track 스킬 구조: callout → heading → DB → FAQ"""
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "✅"), "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": f"📋 {c.get('db_name', bp['main_page']['title'])}", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
    ]
    # FAQ 토글
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    _add_database(bp, c)


def _build_collect(bp: dict, c: dict, bg: str) -> None:
    """Collect 스킬 구조: callout → 2단 칼럼 → DB → toggle"""
    # 좌측 사이드바
    left_blocks: list[dict] = [
        {"type": "heading_2", "text": "Quick Action"},
        {"type": "callout", "text": "새 기록 쓰기", "icon": "✏️", "color": bg},
        {"type": "divider"},
        {"type": "heading_2", "text": "Menu"},
    ]
    for sub in c.get("sub_pages", []):
        left_blocks.append({"type": "bulleted_list", "text": f"{sub.get('icon', '📄')} {sub['name']}"})

    # 우측 메인
    right_blocks: list[dict] = [
        {"type": "heading_1", "text": c.get("db_name", bp["main_page"]["title"]), "color": bg},
        {"type": "callout", "text": "아래에서 컬렉션을 관리하세요", "icon": "👇", "color": bg},
    ]

    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "📝"), "color": bg},
        {"type": "divider"},
        {"type": "column_list", "columns": [{"blocks": left_blocks}, {"blocks": right_blocks}]},
        {"type": "divider"},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
    ]
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    _add_database(bp, c)
    _add_sub_pages(bp, c, bg)


def _build_manage(bp: dict, c: dict, bg: str) -> None:
    """Manage 스킬 구조: callout → heading → DB → toggle"""
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "📊"), "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": f"🗂️ {c.get('db_name', 'Tasks')}", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
    ]
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    _add_database(bp, c)


def _build_plan(bp: dict, c: dict, bg: str) -> None:
    """Plan 스킬 구조: callout → 체크리스트 섹션들 → DB → FAQ"""
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "📅"), "color": bg},
        {"type": "divider"},
    ]

    # 샘플 데이터를 카테고리별로 그룹화하여 체크리스트 생성
    categories = set()
    for item in c.get("sample_items", []):
        for key, val in item.items():
            if key not in ("icon",) and isinstance(val, str) and val in [
                opt.get("name", "") for prop in c.get("db_properties", {}).values()
                if isinstance(prop, dict) for opt in prop.get("options", [])
            ]:
                categories.add(val)

    if categories:
        for cat in sorted(categories):
            bp["blocks"].append({"type": "heading_2", "text": f"📋 {cat}", "color": bg})
            items = [item for item in c.get("sample_items", []) if cat in str(item.values())]
            for item in items[:3]:
                title_val = next((v for k, v in item.items() if k not in ("icon",) and isinstance(v, str) and v != cat), "항목")
                bp["blocks"].append({"type": "to_do", "text": title_val})
    else:
        # 카테고리 없으면 샘플로 체크리스트
        for item in c.get("sample_items", [])[:5]:
            title_val = next((v for k, v in item.items() if k != "icon" and isinstance(v, str)), "항목")
            bp["blocks"].append({"type": "to_do", "text": title_val})

    bp["blocks"].extend([
        {"type": "divider"},
        {"type": "heading_1", "text": f"📊 {c.get('db_name', '상세 계획')}", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
    ])
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    _add_database(bp, c)


def _build_organize(bp: dict, c: dict, bg: str) -> None:
    """Organize 스킬 구조: 2단 칼럼(카테고리+메인) → DB"""
    # 카테고리 목록 추출
    categories = []
    for prop_name, prop_spec in c.get("db_properties", {}).items():
        if isinstance(prop_spec, dict) and prop_spec.get("type") == "select":
            categories = [opt["name"] for opt in prop_spec.get("options", [])]
            break

    left_blocks: list[dict] = [{"type": "heading_2", "text": "📂 Categories", "color": bg}]
    for cat in categories[:8]:
        left_blocks.append({"type": "bulleted_list", "text": cat})

    right_blocks: list[dict] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "🔖"), "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": c.get("db_name", bp["main_page"]["title"]), "color": bg},
        {"type": "callout", "text": "아래에서 정리하세요", "icon": "👇", "color": bg},
    ]

    bp["blocks"] = [
        {"type": "column_list", "columns": [{"blocks": left_blocks}, {"blocks": right_blocks}]},
        {"type": "divider"},
        {"type": "database_ref", "db_index": 0},
    ]

    _add_database(bp, c)


def _build_guide(bp: dict, c: dict, bg: str) -> None:
    """Guide 스킬 구조: callout → 체크리스트 → DB → FAQ"""
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": "👋", "color": bg},
        {"type": "divider"},
    ]

    # 샘플을 체크리스트로
    for i, item in enumerate(c.get("sample_items", [])):
        title_val = next((v for k, v in item.items() if k != "icon" and isinstance(v, str)), f"항목 {i+1}")
        bp["blocks"].append({"type": "to_do", "text": title_val, "checked": i < 2})

    bp["blocks"].extend([
        {"type": "divider"},
        {"type": "heading_1", "text": f"📊 {c.get('db_name', '진행 현황')}", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
        {"type": "heading_2", "text": "💡 자주 묻는 질문", "color": bg},
    ])
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})

    _add_database(bp, c)


def _build_hub(bp: dict, c: dict, bg: str) -> None:
    """Hub 스킬 구조: nav → 2단 칼럼(사이드바+메인) → DB"""
    sub_pages = c.get("sub_pages", [])
    nav_text = " | ".join(["Home"] + [s["name"] for s in sub_pages])

    # 사이드바
    left_blocks: list[dict] = [
        {"type": "callout", "text": "캘린더 뷰는 DB에서 추가하세요 :)", "icon": "💡", "color": bg},
        {"type": "divider"},
    ]

    # 하위 페이지를 섹션별로 그룹
    for i, sub in enumerate(sub_pages):
        if i % 2 == 0:
            section_name = sub.get("description", sub["name"])
            left_blocks.append({"type": "heading_2", "text": section_name, "color": bg})
        left_blocks.append({"type": "bulleted_list", "text": f"{sub.get('icon', '📄')} {sub['name']}"})

    # 메인
    right_blocks: list[dict] = [
        {"type": "heading_1", "text": bp["main_page"]["title"], "color": bg},
        {"type": "divider"},
    ]
    # 액션 콜아웃
    action_texts = ["일정 추가하기", "회의록 추가하기", "새 항목 추가하기"]
    action_icons = ["✅", "🗓️", "📝"]
    for text, icon in zip(action_texts[:3], action_icons[:3]):
        right_blocks.append({"type": "callout", "text": text, "icon": icon, "color": bg})
    right_blocks.append({"type": "divider"})
    right_blocks.append({"type": "callout", "text": "아래 데이터베이스에서 관리하세요", "icon": "👇", "color": bg})

    bp["blocks"] = [
        {"type": "paragraph", "text": nav_text, "color": bg},
        {"type": "divider"},
        {"type": "column_list", "columns": [{"blocks": left_blocks}, {"blocks": right_blocks}]},
        {"type": "divider"},
        {"type": "heading_2", "text": f"📊 {c.get('db_name', bp['main_page']['title'])}", "color": bg},
        {"type": "database_ref", "db_index": 0},
    ]

    _add_database(bp, c)
    _add_sub_pages(bp, c, bg)


# ============================================================
# 공통 헬퍼
# ============================================================

def _add_database(bp: dict, c: dict) -> None:
    """DB 정보를 Blueprint에 추가"""
    views = []
    for v in c.get("views", ["table"]):
        if isinstance(v, str):
            views.append({"type": v, "title": v})
        elif isinstance(v, dict):
            views.append(v)

    bp["databases"].append({
        "title": c.get("db_name", "Items"),
        "is_inline": True,
        "properties": c.get("db_properties", {"이름": "title"}),
        "views": views,
        "sample_items": c.get("sample_items", []),
    })


def _add_sub_pages(bp: dict, c: dict, bg: str) -> None:
    """하위 페이지를 Blueprint에 추가"""
    for sub in c.get("sub_pages", []):
        bp["sub_pages"].append({
            "title": sub["name"],
            "icon": sub.get("icon", "📄"),
            "blocks": [
                {"type": "heading_1", "text": f"{sub.get('icon', '📄')} {sub['name']}", "color": bg},
                {"type": "callout", "text": sub.get("description", f"{sub['name']} 관련 내용을 정리하세요."), "icon": "📌", "color": bg},
                {"type": "divider"},
            ],
        })


def _fallback_blueprint(user_message: str) -> dict[str, Any]:
    """폴백: Mock 분석으로 기본 Blueprint"""
    content = _mock_call(user_message)
    skill_md = load_skill(content["skill"])
    blueprint = _assemble_blueprint(content, skill_md)
    blueprint["metadata"]["generation_method"] = "fallback"
    return blueprint


SKILL_BUILDERS = {
    "track": _build_track,
    "collect": _build_collect,
    "manage": _build_manage,
    "plan": _build_plan,
    "organize": _build_organize,
    "guide": _build_guide,
    "hub": _build_hub,
}
