"""AI Tool Calling 기반 Blueprint Generator (dev-2)

흐름:
1. AI 1회 호출 → 스킬 선택 + 맥락 맞춤 내용 생성
2. 실패 시 → 키워드 기반 맥락 감지 → 스킬별 기본 템플릿 사용
3. 선택된 스킬 .md 구조 + 내용 → Blueprint JSON 조립
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

# ============================================================
# 시스템 프롬프트 (개선)
# ============================================================

SYSTEM_PROMPT = """You are a Notion template design expert.
Given a user request, design a complete Notion template.

## Your Task
1. Select the best skill from: {skills}
2. Generate context-specific database properties, sample data, and views
3. Return ONLY valid JSON

## Rules
- title, callout, db_name, sample names: ALL in Korean
- icon: use context-relevant emoji (🏋️ for exercise, 📚 for books, etc.)
- db_properties: minimum 5 properties matching the user's context
- sample_items: minimum 5 items with ALL property values filled
- views: calendar(if dates), board(if status), gallery(if visual items)

## Example: "운동 기록 만들어줘"
```json
{{
  "skill": "track",
  "title": "운동 기록 일지",
  "icon": "🏋️",
  "color": "orange",
  "callout_text": "매일 운동을 기록하고 건강한 습관을 만들어보세요! 💪",
  "db_name": "운동 기록",
  "db_properties": {{
    "운동명": "title",
    "종류": {{"type": "select", "options": [{{"name": "유산소", "color": "blue"}}, {{"name": "근력", "color": "green"}}, {{"name": "스트레칭", "color": "purple"}}]}},
    "시간(분)": "number",
    "칼로리": "number",
    "날짜": "date",
    "완료": "checkbox"
  }},
  "views": ["calendar", "table"],
  "sample_items": [
    {{"운동명": "아침 러닝 5km", "종류": "유산소", "시간(분)": 30, "칼로리": 300, "날짜": "2026-04-01", "완료": true, "icon": "🏃"}},
    {{"운동명": "스쿼트 4세트", "종류": "근력", "시간(분)": 40, "칼로리": 250, "날짜": "2026-04-02", "완료": false, "icon": "🏋️"}},
    {{"운동명": "요가 플로우", "종류": "스트레칭", "시간(분)": 50, "칼로리": 150, "날짜": "2026-04-03", "완료": true, "icon": "🧘"}},
    {{"운동명": "수영 1km", "종류": "유산소", "시간(분)": 45, "칼로리": 400, "날짜": "2026-04-04", "완료": false, "icon": "🏊"}},
    {{"운동명": "플랭크 3세트", "종류": "근력", "시간(분)": 15, "칼로리": 100, "날짜": "2026-04-05", "완료": true, "icon": "💪"}}
  ],
  "sub_pages": [],
  "faq": [{{"q": "운동 종류를 추가하려면?", "a": "종류 속성 클릭 → 옵션 추가"}}]
}}
```

Now respond with JSON for the user's request:"""


# ============================================================
# 메인 함수
# ============================================================

async def generate_blueprint(user_message: str) -> dict[str, Any]:
    """AI로 Blueprint 생성. 실패 시 스마트 폴백."""
    # AI 시도 (최대 2번)
    for attempt in range(2):
        try:
            ai_content = await _call_ai_for_content(user_message)
            if ai_content and ai_content.get("db_properties"):
                skill_name = ai_content.get("skill", "track")
                skill_md = load_skill(skill_name)
                blueprint = _assemble_blueprint(ai_content, skill_md)
                blueprint["metadata"]["generation_method"] = "ai_dynamic"
                blueprint["metadata"]["skill_used"] = skill_name
                return blueprint
        except Exception as e:
            print(f"[AI Blueprint 시도 {attempt+1} 실패] {e}")

    # 폴백: 스마트 키워드 기반
    print(f"[AI 실패 → 스마트 폴백 사용]")
    content = _smart_fallback(user_message)
    skill_md = load_skill(content["skill"])
    blueprint = _assemble_blueprint(content, skill_md)
    blueprint["metadata"]["generation_method"] = "smart_fallback"
    return blueprint


# ============================================================
# AI 호출
# ============================================================

async def _call_ai_for_content(user_message: str) -> dict[str, Any] | None:
    provider = settings.ai_provider
    prompt = SYSTEM_PROMPT.format(skills=get_tool_enum_description())

    if provider == "groq":
        return await _groq_call(prompt, user_message)
    elif provider == "gemini":
        return await _gemini_call(prompt, user_message)
    elif provider == "claude":
        return await _claude_call(prompt, user_message)
    else:
        return None


async def _groq_call(system: str, user_message: str) -> dict[str, Any] | None:
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
    try:
        from google import genai
        client = genai.Client(api_key=settings.gemini_api_key)
        response = await client.aio.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"{system}\n\nUser request: {user_message}",
        )
        return _parse_json_response(response.text or "")
    except Exception as e:
        print(f"[Gemini 에러] {e}")
        return None


async def _claude_call(system: str, user_message: str) -> dict[str, Any] | None:
    try:
        import anthropic
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model=settings.claude_model,
            max_tokens=2048,
            system=system,
            messages=[{"role": "user", "content": user_message}],
        )
        return _parse_json_response(response.content[0].text)
    except Exception as e:
        print(f"[Claude 에러] {e}")
        return None


def _parse_json_response(text: str) -> dict[str, Any] | None:
    json_match = re.search(r"\{[\s\S]*\}", text)
    if not json_match:
        return None
    try:
        data = json.loads(json_match.group())
        if "skill" in data and "db_properties" in data:
            return data
        return None
    except (json.JSONDecodeError, Exception):
        return None


# ============================================================
# 스마트 폴백 (AI 실패 시 — 키워드 기반 맥락 감지)
# ============================================================

# 맥락별 기본 템플릿
FALLBACK_TEMPLATES: dict[str, dict[str, Any]] = {
    "운동": {
        "skill": "track", "title": "운동 기록 일지", "icon": "🏋️", "color": "orange",
        "callout_text": "매일 운동을 기록하고 건강한 습관을 만들어보세요! 💪",
        "db_name": "운동 기록",
        "db_properties": {
            "운동명": "title",
            "종류": {"type": "select", "options": [{"name": "유산소", "color": "blue"}, {"name": "근력", "color": "green"}, {"name": "스트레칭", "color": "purple"}]},
            "시간(분)": "number", "칼로리": "number", "날짜": "date", "완료": "checkbox",
        },
        "views": ["calendar", "table"],
        "sample_items": [
            {"운동명": "아침 러닝 5km", "종류": "유산소", "시간(분)": 30, "칼로리": 300, "날짜": "2026-04-01", "완료": True, "icon": "🏃"},
            {"운동명": "스쿼트 4세트", "종류": "근력", "시간(분)": 40, "칼로리": 250, "날짜": "2026-04-02", "완료": False, "icon": "🏋️"},
            {"운동명": "요가 플로우", "종류": "스트레칭", "시간(분)": 50, "칼로리": 150, "날짜": "2026-04-03", "완료": True, "icon": "🧘"},
            {"운동명": "수영 1km", "종류": "유산소", "시간(분)": 45, "칼로리": 400, "날짜": "2026-04-04", "완료": False, "icon": "🏊"},
            {"운동명": "플랭크 3세트", "종류": "근력", "시간(분)": 15, "칼로리": 100, "날짜": "2026-04-05", "완료": True, "icon": "💪"},
        ],
        "sub_pages": [], "faq": [{"q": "운동 종류를 추가하려면?", "a": "종류 속성 클릭 → 옵션 추가"}],
    },
    "독서": {
        "skill": "collect", "title": "독서 기록", "icon": "📚", "color": "green",
        "callout_text": "읽은 책을 기록하고 나만의 서재를 만들어보세요! 📖",
        "db_name": "독서 기록",
        "db_properties": {
            "책 제목": "title",
            "저자": "rich_text",
            "장르": {"type": "select", "options": [{"name": "소설", "color": "blue"}, {"name": "자기계발", "color": "green"}, {"name": "기술", "color": "orange"}, {"name": "에세이", "color": "purple"}]},
            "상태": "status", "평점": "number", "날짜": "date", "메모": "rich_text",
        },
        "views": ["gallery", "table"],
        "sample_items": [
            {"책 제목": "원씽", "저자": "게리 켈러", "장르": "자기계발", "평점": 4, "날짜": "2026-03-15", "icon": "📕"},
            {"책 제목": "클린 코드", "저자": "로버트 마틴", "장르": "기술", "평점": 5, "날짜": "2026-03-20", "icon": "📘"},
            {"책 제목": "데미안", "저자": "헤르만 헤세", "장르": "소설", "평점": 4, "날짜": "2026-03-25", "icon": "📗"},
            {"책 제목": "아토믹 해빗", "저자": "제임스 클리어", "장르": "자기계발", "평점": 5, "날짜": "2026-03-28", "icon": "📙"},
            {"책 제목": "나는 나로 살기로 했다", "저자": "김수현", "장르": "에세이", "평점": 3, "날짜": "2026-04-01", "icon": "📔"},
        ],
        "sub_pages": [{"name": "읽고 싶은 책", "icon": "📚", "description": "읽을 책 목록"}],
        "faq": [{"q": "평점은 어떻게 매기나요?", "a": "1~5점으로 자유롭게 평가하세요"}],
    },
    "프로젝트": {
        "skill": "manage", "title": "프로젝트 보드", "icon": "📊", "color": "blue",
        "callout_text": "프로젝트 진행 현황을 한눈에 관리하세요! 🗂️",
        "db_name": "프로젝트 태스크",
        "db_properties": {
            "태스크": "title", "상태": "status",
            "담당자": "rich_text",
            "우선순위": {"type": "select", "options": [{"name": "높음", "color": "red"}, {"name": "중간", "color": "yellow"}, {"name": "낮음", "color": "green"}]},
            "기한": "date", "카테고리": {"type": "select", "options": [{"name": "기획", "color": "blue"}, {"name": "개발", "color": "green"}, {"name": "디자인", "color": "purple"}, {"name": "QA", "color": "orange"}]},
        },
        "views": ["board", "timeline", "table"],
        "sample_items": [
            {"태스크": "기획서 작성", "담당자": "김팀장", "우선순위": "높음", "기한": "2026-04-05", "카테고리": "기획", "icon": "📝"},
            {"태스크": "UI 디자인", "담당자": "이디자이너", "우선순위": "높음", "기한": "2026-04-10", "카테고리": "디자인", "icon": "🎨"},
            {"태스크": "백엔드 API", "담당자": "박개발", "우선순위": "중간", "기한": "2026-04-15", "카테고리": "개발", "icon": "⚙️"},
            {"태스크": "프론트엔드 구현", "담당자": "최개발", "우선순위": "중간", "기한": "2026-04-18", "카테고리": "개발", "icon": "🖥️"},
            {"태스크": "QA 테스트", "담당자": "정QA", "우선순위": "낮음", "기한": "2026-04-22", "카테고리": "QA", "icon": "🧪"},
        ],
        "sub_pages": [], "faq": [{"q": "칸반 보드로 보려면?", "a": "DB 상단 보드 뷰 탭 클릭"}],
    },
    "일정": {
        "skill": "plan", "title": "일정 관리", "icon": "📅", "color": "blue",
        "callout_text": "일정을 체계적으로 관리하세요! 📅",
        "db_name": "일정",
        "db_properties": {
            "일정명": "title", "날짜": "date", "카테고리": {"type": "select", "options": [{"name": "미팅", "color": "blue"}, {"name": "업무", "color": "green"}, {"name": "개인", "color": "purple"}]},
            "완료": "checkbox", "메모": "rich_text",
        },
        "views": ["calendar", "table"],
        "sample_items": [
            {"일정명": "팀 주간 미팅", "날짜": "2026-04-01", "카테고리": "미팅", "완료": True, "icon": "🗓️"},
            {"일정명": "기획서 마감", "날짜": "2026-04-03", "카테고리": "업무", "완료": False, "icon": "📋"},
            {"일정명": "클라이언트 미팅", "날짜": "2026-04-05", "카테고리": "미팅", "완료": False, "icon": "🤝"},
            {"일정명": "코드 리뷰", "날짜": "2026-04-07", "카테고리": "업무", "완료": False, "icon": "💻"},
            {"일정명": "헬스장", "날짜": "2026-04-08", "카테고리": "개인", "완료": False, "icon": "🏋️"},
        ],
        "sub_pages": [], "faq": [],
    },
    "대시보드": {
        "skill": "hub", "title": "팀 대시보드", "icon": "🏢", "color": "purple",
        "callout_text": "팀의 모든 활동을 한눈에 관리하세요!",
        "db_name": "활동 목록",
        "db_properties": {
            "항목": "title", "날짜": "date", "상태": "status",
            "담당자": "rich_text",
            "태그": {"type": "multi_select", "options": [{"name": "회의", "color": "blue"}, {"name": "업무", "color": "green"}, {"name": "공지", "color": "orange"}]},
        },
        "views": ["calendar", "board", "table"],
        "sample_items": [
            {"항목": "주간 회의", "날짜": "2026-04-01", "태그": "회의", "icon": "📋"},
            {"항목": "분기 목표 설정", "날짜": "2026-04-03", "태그": "업무", "icon": "🎯"},
            {"항목": "신입 온보딩", "날짜": "2026-04-05", "태그": "공지", "icon": "👋"},
            {"항목": "코드 리뷰", "날짜": "2026-04-07", "태그": "업무", "icon": "💻"},
            {"항목": "팀 회식", "날짜": "2026-04-10", "태그": "공지", "icon": "🍽️"},
        ],
        "sub_pages": [
            {"name": "Members", "icon": "👥", "description": "팀원 목록"},
            {"name": "Calendar", "icon": "📅", "description": "일정 관리"},
            {"name": "Projects", "icon": "📋", "description": "프로젝트 관리"},
        ],
        "faq": [],
    },
}

# 키워드 → 폴백 템플릿 매핑
FALLBACK_KEYWORDS: dict[str, list[str]] = {
    "운동": ["운동", "헬스", "피트니스", "트레이닝", "러닝", "조깅", "웨이트"],
    "독서": ["독서", "책", "도서", "읽기", "서평", "북리뷰"],
    "프로젝트": ["프로젝트", "태스크", "칸반", "스프린트", "업무", "관리", "보드"],
    "일정": ["일정", "스케줄", "캘린더", "계획", "준비", "여행", "결혼"],
    "대시보드": ["대시보드", "홈", "메인", "팀", "워크스페이스"],
}


def _smart_fallback(user_message: str) -> dict[str, Any]:
    """AI 실패 시 키워드 기반 맥락 감지 → 품질 높은 폴백"""
    msg = user_message.lower()

    # 키워드 매칭으로 적합한 폴백 템플릿 선택
    for template_key, keywords in FALLBACK_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            template = FALLBACK_TEMPLATES[template_key].copy()
            # 제목에 유저 맥락 반영
            clean_title = user_message.replace("만들어줘", "").replace("만들어", "").replace("제작해줘", "").replace("!", "").replace("매우 자세하게 제작해줘야돼", "").strip()
            if clean_title and len(clean_title) < 30:
                template["title"] = clean_title
            return template

    # 매칭 안 되면 스킬 레지스트리에서 검색
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

    # 스킬 기반 기본 템플릿
    defaults = FALLBACK_TEMPLATES.get("일정", FALLBACK_TEMPLATES["운동"]).copy()
    defaults["skill"] = skill
    defaults["color"] = color
    clean_title = user_message.replace("만들어줘", "").replace("제작해줘", "").replace("!", "").strip()
    if clean_title and len(clean_title) < 30:
        defaults["title"] = clean_title
    return defaults


# ============================================================
# Blueprint 조립
# ============================================================

def _assemble_blueprint(content: dict, skill_md: str | None) -> dict[str, Any]:
    skill = content.get("skill", "track")
    color = content.get("color", "gray")
    bg = f"{color}_background" if color != "default" else "default"
    title = content.get("title", "My Template")

    blueprint: dict[str, Any] = {
        "version": "2.0",
        "metadata": {"title": title, "template_type": skill, "color_theme": color},
        "main_page": {"title": title, "icon": content.get("icon", "📋"), "cover_url": COVER_URLS.get(color, COVER_URLS["default"])},
        "blocks": [], "databases": [], "sub_pages": [],
    }

    builder = SKILL_BUILDERS.get(skill, _build_track)
    builder(blueprint, content, bg)
    return blueprint


# ============================================================
# 스킬별 구조 빌더 (변경 없음)
# ============================================================

def _build_track(bp: dict, c: dict, bg: str) -> None:
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "✅"), "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": f"📋 {c.get('db_name', bp['main_page']['title'])}", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
    ]
    for faq in c.get("faq", []):
        bp["blocks"].append({"type": "toggle", "text": faq["q"], "children_text": faq["a"]})
    _add_database(bp, c)


def _build_collect(bp: dict, c: dict, bg: str) -> None:
    left_blocks: list[dict] = [
        {"type": "heading_2", "text": "Quick Action"},
        {"type": "callout", "text": "새 기록 쓰기", "icon": "✏️", "color": bg},
        {"type": "divider"},
        {"type": "heading_2", "text": "Menu"},
    ]
    for sub in c.get("sub_pages", []):
        left_blocks.append({"type": "bulleted_list", "text": f"{sub.get('icon', '📄')} {sub['name']}"})
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
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": c.get("icon", "📅"), "color": bg},
        {"type": "divider"},
    ]
    for i, item in enumerate(c.get("sample_items", [])[:5]):
        title_val = next((v for k, v in item.items() if k != "icon" and isinstance(v, str)), f"항목 {i+1}")
        bp["blocks"].append({"type": "to_do", "text": title_val, "checked": i < 2})
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
    categories = []
    for prop_spec in c.get("db_properties", {}).values():
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
    ]
    bp["blocks"] = [
        {"type": "column_list", "columns": [{"blocks": left_blocks}, {"blocks": right_blocks}]},
        {"type": "divider"},
        {"type": "database_ref", "db_index": 0},
    ]
    _add_database(bp, c)


def _build_guide(bp: dict, c: dict, bg: str) -> None:
    bp["blocks"] = [
        {"type": "callout", "text": c.get("callout_text", ""), "icon": "👋", "color": bg},
        {"type": "divider"},
    ]
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
    sub_pages = c.get("sub_pages", [])
    nav_text = " | ".join(["Home"] + [s["name"] for s in sub_pages])
    left_blocks: list[dict] = [
        {"type": "callout", "text": "캘린더 뷰는 DB에서 추가하세요 :)", "icon": "💡", "color": bg},
        {"type": "divider"},
    ]
    for i, sub in enumerate(sub_pages):
        if i % 2 == 0:
            left_blocks.append({"type": "heading_2", "text": sub.get("description", sub["name"]), "color": bg})
        left_blocks.append({"type": "bulleted_list", "text": f"{sub.get('icon', '📄')} {sub['name']}"})
    right_blocks: list[dict] = [
        {"type": "heading_1", "text": bp["main_page"]["title"], "color": bg},
        {"type": "divider"},
        {"type": "callout", "text": "일정 추가하기", "icon": "✅", "color": bg},
        {"type": "callout", "text": "회의록 추가하기", "icon": "🗓️", "color": bg},
        {"type": "divider"},
        {"type": "callout", "text": "아래 데이터베이스에서 관리하세요", "icon": "👇", "color": bg},
    ]
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
    for sub in c.get("sub_pages", []):
        bp["sub_pages"].append({
            "title": sub["name"], "icon": sub.get("icon", "📄"),
            "blocks": [
                {"type": "heading_1", "text": f"{sub.get('icon', '📄')} {sub['name']}", "color": bg},
                {"type": "callout", "text": sub.get("description", f"{sub['name']} 관련 내용을 정리하세요."), "icon": "📌", "color": bg},
                {"type": "divider"},
            ],
        })


SKILL_BUILDERS = {
    "track": _build_track, "collect": _build_collect, "manage": _build_manage,
    "plan": _build_plan, "organize": _build_organize, "guide": _build_guide, "hub": _build_hub,
}
