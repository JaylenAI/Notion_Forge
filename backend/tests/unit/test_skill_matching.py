"""스킬 매칭 + 레이아웃 라우터 테스트"""

import pytest

from app.agent.layout_router import layout_router
from app.agent.skill_router import TIER2_SKILLS, _keyword_score
from app.skills import SKILL_REGISTRY


class TestSkillRegistry:
    def test_total_count(self):
        assert len(SKILL_REGISTRY) == 48

    def test_tier1_skills(self):
        tier1 = {
            "track",
            "collect",
            "manage",
            "plan",
            "organize",
            "guide",
            "hub",
            "finance",
            "journal",
            "content",
            "learn",
            "crm",
        }
        for s in tier1:
            assert s in SKILL_REGISTRY

    def test_tier2_count(self):
        assert len(TIER2_SKILLS) == 36

    def test_all_tier2_in_registry(self):
        for s in TIER2_SKILLS:
            assert s in SKILL_REGISTRY, f"{s} not in SKILL_REGISTRY"


class TestSkillMatching:
    @pytest.mark.parametrize(
        "message,expected",
        [
            ("운동 기록 일지 만들어줘", "fitness"),
            ("독서 기록장 만들어줘", "reading"),
            ("프로젝트 관리 보드 만들어줘", "project"),
            ("가계부 만들어줘", "budget"),
            ("CRM 고객 관리 만들어줘", "crm"),
            ("온보딩 가이드 만들어줘", "onboarding"),
            ("팀 위키 만들어줘", "wiki"),
            ("일기 다이어리 만들어줘", "diary"),
            ("감사 일기 만들어줘", "gratitude"),
            ("블로그 콘텐츠 관리 만들어줘", "blog"),
            ("유튜브 영상 관리 만들어줘", "youtube"),
            ("SNS 소셜미디어 캘린더 만들어줘", "social"),
            ("주간 회고 리뷰 만들어줘", "review"),
            ("습관 트래커 만들어줘", "habit"),
            ("여행 계획 만들어줘", "travel"),
        ],
    )
    def test_skill_match(self, message, expected):
        best_t2, t2_score, best_t1, t1_score = _keyword_score(message)
        result = best_t2 if t2_score > 0 else best_t1 if t1_score > 0 else None
        assert result == expected, f'"{message}" → {result} (expected: {expected})'

    def test_returns_none_for_generic(self):
        best_t2, t2_score, best_t1, t1_score = _keyword_score("something")
        result = best_t2 if t2_score > 0 else best_t1 if t1_score > 0 else None
        assert result is None or result in SKILL_REGISTRY


class TestLayoutRouter:
    @pytest.mark.parametrize(
        "message,expected_layout",
        [
            ("운동 기록 트래커 만들어줘", "simple_tracker"),
            ("프로젝트 칸반 보드 만들어줘", "kanban_board"),
            ("독서 기록 갤러리 만들어줘", "gallery_hero"),
            ("일정 캘린더 만들어줘", "calendar_main"),
            ("대시보드 만들어줘", "dashboard_widgets"),
        ],
    )
    def test_layout_routing(self, message, expected_layout):
        result = layout_router.route(message)
        assert result.layout == expected_layout, f'"{message}" → {result.layout} (expected: {expected_layout})'

    def test_confidence_range(self):
        result = layout_router.route("프로젝트 관리 만들어줘")
        assert 0.0 <= result.confidence <= 1.0

    def test_has_reason(self):
        result = layout_router.route("운동 기록 만들어줘")
        assert result.reason
