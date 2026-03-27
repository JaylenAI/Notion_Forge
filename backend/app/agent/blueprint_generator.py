"""의도 분석 결과 → Template Blueprint JSON 생성 (스킬 기반)"""

from typing import Any

from app.schemas.blueprint import IntentResult
from app.skills import load_skill


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

TEMPLATE_ICONS: dict[str, str] = {
    "dashboard": "🏢", "tracker": "✅", "bookmark": "🔖",
    "project": "📊", "note": "📝", "onboarding": "👋",
    "crm": "🤝", "custom": "⚡",
}


def generate_blueprint(intent: IntentResult) -> dict[str, Any]:
    """의도 분석 결과를 기반으로 Template Blueprint 생성"""
    template_type = intent.template_type
    color = intent.color_theme if intent.color_theme != "default" else "gray"
    bg = f"{color}_background" if color != "default" else "default"

    # 스킬 파일 로드 (존재 확인용)
    skill_content = load_skill(template_type)

    bp: dict[str, Any] = {
        "version": "1.0",
        "metadata": {
            "title": intent.title or "My Workspace",
            "template_type": template_type,
            "color_theme": color,
            "skill_loaded": skill_content is not None,
        },
        "main_page": {
            "title": intent.title or "My Workspace",
            "icon": TEMPLATE_ICONS.get(template_type, "⚡"),
            "cover_url": COVER_URLS.get(color, COVER_URLS["default"]),
        },
        "blocks": [],
        "databases": [],
        "sub_pages": [],
    }

    builder = BUILDERS.get(template_type, _build_custom)
    builder(bp, intent, bg, color)
    return bp


# ============================================================
# 대시보드 (이미지 수준 고도화)
# ============================================================

def _build_dashboard(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    title = intent.title or "To-Do List"

    # 메인 DB
    bp["databases"].append({
        "title": title,
        "is_inline": True,
        "properties": {
            "이름": "title",
            "날짜": "date",
            "설명": "rich_text",
            "진행사항": "status",
            "태그": {"type": "multi_select", "options": [
                {"name": "ETC", "color": "yellow"},
                {"name": "Study", "color": "blue"},
                {"name": "Meeting", "color": "purple"},
                {"name": "To-Do List", "color": "orange"},
            ]},
        },
        "sample_items": [
            {"이름": "고객사 출장", "날짜": "2026-01-12", "태그": "ETC", "icon": "⭐"},
            {"이름": "노션팀 1주차 스터디", "날짜": "2026-01-13", "태그": "Study", "icon": "📌"},
            {"이름": "노션팀 주간 미팅", "날짜": "2026-01-15", "태그": "Meeting", "icon": "📁"},
            {"이름": "마케팅 홍보 자료 제작하기", "날짜": "2026-01-16", "태그": "To-Do List", "icon": "⬜"},
        ],
    })

    # 하위 페이지 (네비게이션용)
    sub_names = intent.sub_pages or ["Members", "Calendar", "Project", "Study"]
    sub_icons = {"Members": "👥", "Calendar": "📅", "Project": "📋", "Study": "📖"}

    # 좌측 사이드바 블록
    sidebar: list[dict] = [
        {"type": "callout", "text": "캘린더 뷰는 DB에서 직접 추가해주세요 :)", "icon": "💡", "color": bg},
        {"type": "divider"},
    ]

    # 사이드바 섹션들
    sections = {
        "Team": ["Members", "Calendar"],
        "Project": ["Project"],
        "Study": ["Study"],
    }
    for section_name, items in sections.items():
        sidebar.append({"type": "heading_2", "text": section_name, "color": bg})
        for item in items:
            icon = sub_icons.get(item, "📄")
            sidebar.append({"type": "bulleted_list", "text": f"{icon} {item}"})
        sidebar.append({"type": "paragraph", "text": ""})

    # 우측 메인 블록
    main_content: list[dict] = [
        {"type": "heading_1", "text": title, "color": bg},
        {"type": "divider"},
    ]

    # 액션 버튼 (콜아웃으로 대체 - 4개 가로 배치)
    action_buttons: list[dict] = [
        {"type": "callout", "text": "To Do List 추가하기", "icon": "✅", "color": bg},
        {"type": "callout", "text": "회의록 추가하기", "icon": "🗓️", "color": bg},
        {"type": "callout", "text": "스터디 일정 추가하기", "icon": "📋", "color": bg},
        {"type": "callout", "text": "기타 일정 추가하기", "icon": "📝", "color": bg},
    ]

    # 액션 버튼을 콜아웃으로 세로 배치 (칼럼 중첩 불가)
    for btn in action_buttons:
        main_content.append(btn)

    main_content.append({"type": "divider"})
    # DB는 칼럼 안에 넣을 수 없으므로, 칼럼 아래에 별도 배치
    main_content.append({"type": "callout", "text": "📊 아래 데이터베이스에서 일정을 관리하세요", "icon": "👇", "color": bg})

    # 네비게이션 바 (상단)
    nav_text = " | ".join(["Home"] + sub_names)
    bp["blocks"] = [
        {"type": "paragraph", "text": nav_text, "color": bg},
        {"type": "divider"},
        {"type": "column_list", "columns": [
            {"blocks": sidebar},
            {"blocks": main_content},
        ]},
        {"type": "divider"},
        {"type": "heading_2", "text": f"📊 {title}", "color": bg},
        {"type": "database_ref", "db_index": 0},
    ]

    # 하위 페이지
    for name in sub_names:
        icon = sub_icons.get(name, "📄")
        bp["sub_pages"].append({
            "title": name,
            "icon": icon,
            "blocks": [
                {"type": "heading_1", "text": f"{icon} {name}", "color": bg},
                {"type": "callout", "text": f"{name} 관련 내용을 여기에 정리하세요.", "icon": "📌", "color": bg},
                {"type": "divider"},
                {"type": "paragraph", "text": ""},
            ],
        })


# ============================================================
# 트래커
# ============================================================

def _build_tracker(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    bp["databases"].append({
        "title": intent.title or "습관 트래커",
        "is_inline": True,
        "properties": {
            "항목": "title",
            "카테고리": {"type": "select", "options": [
                {"name": "건강", "color": "green"},
                {"name": "학습", "color": "blue"},
                {"name": "생활", "color": "orange"},
                {"name": "자기계발", "color": "purple"},
            ]},
            "완료": "checkbox",
            "날짜": "date",
            "메모": "rich_text",
        },
        "sample_items": [
            {"항목": "운동 30분", "카테고리": "건강", "icon": "💪"},
            {"항목": "독서 1시간", "카테고리": "학습", "icon": "📚"},
            {"항목": "명상 10분", "카테고리": "건강", "icon": "🧘"},
            {"항목": "영어 공부", "카테고리": "학습", "icon": "🇺🇸"},
            {"항목": "물 2L 마시기", "카테고리": "생활", "icon": "💧"},
        ],
    })

    bp["blocks"] = [
        {"type": "callout", "text": "매일 체크하며 습관을 만들어보세요! 작은 습관이 큰 변화를 만듭니다.", "icon": "🎯", "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": "📋 오늘의 할 일", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
        {"type": "toggle", "text": "💡 사용법", "children_text": "매일 아침 이 페이지를 열고, 완료한 항목에 체크하세요. 카테고리별로 필터링도 가능합니다."},
    ]


# ============================================================
# 북마크
# ============================================================

def _build_bookmark(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    categories = ["커리어", "쇼핑", "교육/툴", "뉴스", "엔터"]

    bp["databases"].append({
        "title": "북마크",
        "is_inline": True,
        "properties": {
            "이름": "title",
            "URL": "url",
            "카테고리": {"type": "select", "options": [
                {"name": "커리어", "color": "blue"},
                {"name": "쇼핑", "color": "red"},
                {"name": "교육/툴", "color": "green"},
                {"name": "뉴스", "color": "orange"},
                {"name": "엔터", "color": "purple"},
            ]},
            "즐겨찾기": "checkbox",
            "메모": "rich_text",
        },
        "sample_items": [
            {"이름": "Google", "icon": "🔍"},
            {"이름": "GitHub", "icon": "🐙"},
            {"이름": "Notion", "icon": "📓"},
            {"이름": "Figma", "icon": "🎨"},
            {"이름": "YouTube", "icon": "📺"},
        ],
    })

    sidebar: list[dict] = [{"type": "heading_2", "text": "📂 Category", "color": bg}]
    for cat in categories:
        sidebar.append({"type": "bulleted_list", "text": cat})

    main_content: list[dict] = [
        {"type": "callout", "text": "즐겨찾기에 체크하면 자주 쓰는 사이트를 빠르게 찾을 수 있어요.", "icon": "⭐", "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": "🔖 북마크", "color": bg},
        {"type": "database_ref", "db_index": 0},
    ]

    bp["blocks"] = [
        {"type": "column_list", "columns": [
            {"blocks": sidebar},
            {"blocks": main_content},
        ]},
    ]


# ============================================================
# 프로젝트
# ============================================================

def _build_project(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    bp["databases"].append({
        "title": "Tasks",
        "is_inline": True,
        "properties": {
            "태스크": "title",
            "상태": "status",
            "담당자": "rich_text",
            "우선순위": {"type": "select", "options": [
                {"name": "높음", "color": "red"},
                {"name": "중간", "color": "yellow"},
                {"name": "낮음", "color": "green"},
            ]},
            "기한": "date",
        },
        "sample_items": [
            {"태스크": "기획서 작성", "icon": "📝"},
            {"태스크": "디자인 시안", "icon": "🎨"},
            {"태스크": "백엔드 개발", "icon": "⚙️"},
            {"태스크": "프론트 개발", "icon": "🖥️"},
            {"태스크": "QA 테스트", "icon": "🧪"},
        ],
    })

    bp["blocks"] = [
        {"type": "callout", "text": "프로젝트 진행 현황을 한눈에 관리하세요.", "icon": "📊", "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": "🗂️ 태스크 보드", "color": bg},
        {"type": "database_ref", "db_index": 0},
    ]


# ============================================================
# 노트 (Tea Note 스타일)
# ============================================================

def _build_note(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    bp["databases"].append({
        "title": intent.title or "기록",
        "is_inline": True,
        "properties": {
            "이름": "title",
            "종류": {"type": "select", "options": [
                {"name": "기록", "color": "blue"},
                {"name": "메모", "color": "green"},
                {"name": "아이디어", "color": "purple"},
            ]},
            "즐겨찾기": "checkbox",
            "평점": "number",
            "날짜": "date",
        },
        "sample_items": [
            {"이름": "첫 번째 기록", "icon": "📝"},
            {"이름": "좋은 아이디어", "icon": "💡"},
            {"이름": "메모 정리", "icon": "📋"},
        ],
    })

    sidebar: list[dict] = [
        {"type": "heading_2", "text": "Quick Action"},
        {"type": "callout", "text": "새 기록 쓰기", "icon": "✏️", "color": bg},
        {"type": "callout", "text": "일기 쓰기", "icon": "📓", "color": bg},
        {"type": "divider"},
        {"type": "heading_2", "text": "Menu"},
        {"type": "bulleted_list", "text": "📦 인벤토리"},
        {"type": "bulleted_list", "text": "📓 일기장"},
    ]

    main_content: list[dict] = [
        {"type": "callout", "text": "사용 설명서를 읽고 시작해보세요!", "icon": "👀", "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": "기록", "color": bg},
        {"type": "database_ref", "db_index": 0},
    ]

    bp["blocks"] = [
        {"type": "column_list", "columns": [
            {"blocks": sidebar},
            {"blocks": main_content},
        ]},
    ]

    bp["sub_pages"] = [
        {"title": "인벤토리", "icon": "📦", "blocks": [
            {"type": "heading_1", "text": "📦 인벤토리", "color": bg},
            {"type": "callout", "text": "아이템을 정리하세요.", "icon": "📌", "color": bg},
        ]},
        {"title": "일기장", "icon": "📓", "blocks": [
            {"type": "heading_1", "text": "📓 일기장", "color": bg},
            {"type": "callout", "text": "오늘의 이야기를 적어보세요.", "icon": "✏️", "color": bg},
        ]},
    ]


# ============================================================
# 온보딩
# ============================================================

def _build_onboarding(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    bp["databases"].append({
        "title": "인수인계 현황",
        "is_inline": True,
        "properties": {
            "항목": "title",
            "담당자": "rich_text",
            "상태": "status",
            "기한": "date",
        },
        "sample_items": [
            {"항목": "DB 접근권한 발급", "icon": "🔑"},
            {"항목": "코드리뷰 프로세스 안내", "icon": "📖"},
            {"항목": "배포 프로세스 안내", "icon": "🚀"},
        ],
    })

    blocks: list[dict] = [
        {"type": "callout", "text": "환영합니다! 이 페이지는 신입사원 온보딩 가이드입니다.", "icon": "👋", "color": bg},
        {"type": "divider"},
    ]

    weeks = [
        ("1주차", ["계정 발급 (이메일, Slack, Jira)", "팀 미팅 참석", "개발환경 세팅"]),
        ("2주차", ["코드베이스 탐색", "첫 PR 작성", "코드 리뷰 참여"]),
        ("3주차", ["독립 태스크 수행", "문서 정리"]),
        ("4주차", ["프로젝트 배정", "온보딩 회고"]),
    ]
    for week, items in weeks:
        blocks.append({"type": "heading_2", "text": f"📋 {week}", "color": bg})
        for item in items:
            blocks.append({"type": "to_do", "text": item})

    blocks.extend([
        {"type": "divider"},
        {"type": "heading_1", "text": "📊 인수인계 현황", "color": bg},
        {"type": "database_ref", "db_index": 0},
        {"type": "divider"},
        {"type": "heading_2", "text": "💡 자주 묻는 질문", "color": bg},
        {"type": "toggle", "text": "Wi-Fi 비밀번호는?", "children_text": "관리팀에 문의해주세요."},
        {"type": "toggle", "text": "연차 신청 방법은?", "children_text": "HR 시스템에서 신청 가능합니다."},
        {"type": "toggle", "text": "장비 요청은?", "children_text": "IT팀 Slack 채널에 요청하세요."},
    ])

    bp["blocks"] = blocks


# ============================================================
# CRM
# ============================================================

def _build_crm(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    bp["databases"].append({
        "title": "고객 목록",
        "is_inline": True,
        "properties": {
            "고객명": "title",
            "회사": "rich_text",
            "상태": {"type": "select", "options": [
                {"name": "리드", "color": "gray"},
                {"name": "미팅", "color": "blue"},
                {"name": "제안", "color": "orange"},
                {"name": "계약", "color": "green"},
            ]},
            "연락처": "email",
            "최근 연락": "date",
            "메모": "rich_text",
        },
        "sample_items": [
            {"고객명": "김철수", "icon": "👤"},
            {"고객명": "이영희", "icon": "👤"},
            {"고객명": "박지수", "icon": "👤"},
        ],
    })

    bp["blocks"] = [
        {"type": "callout", "text": "고객 관리를 체계적으로!", "icon": "🤝", "color": bg},
        {"type": "divider"},
        {"type": "heading_1", "text": "📋 고객 목록", "color": bg},
        {"type": "database_ref", "db_index": 0},
    ]


# ============================================================
# 커스텀
# ============================================================

def _build_custom(bp: dict, intent: IntentResult, bg: str, color: str) -> None:
    bp["blocks"] = [
        {"type": "callout", "text": "원하는 내용을 자유롭게 구성하세요.", "icon": "⚡", "color": bg},
        {"type": "divider"},
        {"type": "heading_2", "text": "📌 시작하기"},
        {"type": "paragraph", "text": "여기에 내용을 추가하세요."},
    ]


BUILDERS = {
    "dashboard": _build_dashboard,
    "tracker": _build_tracker,
    "bookmark": _build_bookmark,
    "project": _build_project,
    "note": _build_note,
    "onboarding": _build_onboarding,
    "crm": _build_crm,
    "custom": _build_custom,
}
