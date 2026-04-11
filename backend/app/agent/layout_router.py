"""Layout Router: 유저 의도 → 8개 레이아웃 타입 자동 매핑

레이아웃 타입:
- sidebar_main: 사이드바 + 메인 (기본값, 범용)
- gallery_hero: 갤러리가 메인 (일기, 저널, 컬렉션, 레시피)
- category_hub: 카테고리 허브 (회사, 온보딩, 가이드, 위키)
- kanban_board: 칸반 보드 메인 (프로젝트, 태스크, 스프린트)
- calendar_main: 캘린더 메인 (일정, 콘텐츠 캘린더)
- dashboard_widgets: 대시보드 위젯형 (CRM, 분석, KPI)
- simple_tracker: 심플 트래커 (물, 운동, 습관, 수면)
- portfolio: 포트폴리오/이력서 (포트폴리오, 이력서, 소개)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LayoutResult:
    """레이아웃 라우팅 결과"""
    layout: str
    confidence: float
    reason: str


# 키워드 → 레이아웃 매핑 (우선순위 순)
LAYOUT_KEYWORDS: dict[str, list[str]] = {
    "simple_tracker": [
        "물", "물마신", "수면", "습관", "운동", "헬스", "피트니스", "걸음", "체중",
        "트래커", "tracker", "체크", "루틴", "다이어트", "칼로리", "식단",
        "매일", "출석", "streak", "daily",
    ],
    "gallery_hero": [
        "일기", "다이어리", "저널", "journal", "diary", "감사", "무드",
        "레시피", "요리", "맛집", "음식", "카페",
        "와인", "시음", "독서", "책", "도서", "영화", "음악", "앨범",
        "컬렉션", "collection", "수집", "아카이브",
        "사진", "photo", "gallery",
    ],
    "kanban_board": [
        "프로젝트", "project", "태스크", "task", "칸반", "kanban",
        "스프린트", "sprint", "이슈", "issue", "버그", "bug",
        "릴리즈", "release", "개발", "dev", "업무", "work",
        "agile", "scrum", "backlog",
    ],
    "calendar_main": [
        "캘린더", "calendar", "일정", "schedule", "스케줄",
        "콘텐츠 캘린더", "편집", "발행", "마감",
        "수업", "시간표", "timetable",
    ],
    "dashboard_widgets": [
        "대시보드", "dashboard", "crm", "CRM",
        "영업", "세일즈", "sales", "리드", "lead",
        "kpi", "KPI", "분석", "analytics", "통계",
        "매출", "revenue", "전환율",
    ],
    "category_hub": [
        "온보딩", "onboarding", "인수인계", "매뉴얼", "manual",
        "가이드", "guide", "위키", "wiki", "FAQ",
        "회사", "팀", "team", "워크스페이스", "workspace",
        "허브", "hub", "포탈", "portal", "홈", "home",
    ],
    "portfolio": [
        "포트폴리오", "portfolio", "이력서", "resume", "cv",
        "자기소개", "소개", "프로필", "profile",
        "작품", "작업물", "showcase",
    ],
}

# sidebar_main은 기본값이므로 키워드 매핑 불필요


class LayoutRouter:
    """유저 메시지를 분석하여 최적 레이아웃 타입을 결정"""

    @staticmethod
    def route(user_message: str) -> LayoutResult:
        """키워드 기반 레이아웃 라우팅

        Returns:
            LayoutResult with layout name, confidence, and reason
        """
        msg = user_message.lower()

        best_layout = "sidebar_main"
        best_score = 0
        best_matches: list[str] = []

        for layout, keywords in LAYOUT_KEYWORDS.items():
            matches = [kw for kw in keywords if kw in msg]
            score = len(matches)
            if score > best_score:
                best_score = score
                best_layout = layout
                best_matches = matches

        if best_score == 0:
            return LayoutResult(
                layout="sidebar_main",
                confidence=0.5,
                reason="기본 레이아웃 (매칭 키워드 없음)",
            )

        confidence = min(0.95, 0.6 + best_score * 0.1)
        return LayoutResult(
            layout=best_layout,
            confidence=confidence,
            reason=f"키워드 매칭: {', '.join(best_matches[:3])}",
        )

    @staticmethod
    def available_layouts() -> list[str]:
        """사용 가능한 레이아웃 목록"""
        return [
            "sidebar_main",
            "gallery_hero",
            "category_hub",
            "kanban_board",
            "calendar_main",
            "dashboard_widgets",
            "simple_tracker",
            "portfolio",
        ]


# 싱글턴 인스턴스
layout_router = LayoutRouter()
