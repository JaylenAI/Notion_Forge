"""SkillRouter 단위 테스트: 키워드 매칭 + LLM 분류 하이브리드"""

from unittest.mock import AsyncMock

import pytest

from app.agent.skill_router import (
    SkillMatch,
    _extract_skill_essentials,
    _keyword_score,
    build_skill_guide,
    route_skill,
)


class TestKeywordScore:
    def test_fitness_high_score(self):
        best_t2, t2_score, _, _ = _keyword_score("헬스 운동 피트니스 기록")
        assert best_t2 == "fitness"
        assert t2_score >= 2

    def test_reading_match(self):
        best_t2, t2_score, _, _ = _keyword_score("독서 기록장 만들어줘 책")
        assert best_t2 == "reading"
        assert t2_score >= 2

    def test_project_match(self):
        best_t2, t2_score, _, _ = _keyword_score("프로젝트 태스크 관리 보드")
        assert best_t2 == "project"
        assert t2_score >= 2

    def test_tier1_fallback(self):
        _, t2_score, best_t1, t1_score = _keyword_score("관리 시스템")
        assert best_t1 == "manage"
        assert t1_score >= 1

    def test_no_match(self):
        best_t2, t2_score, best_t1, t1_score = _keyword_score("xyz 아무것도 아닌 것")
        assert t2_score == 0
        assert t1_score == 0

    def test_budget_specific(self):
        best_t2, t2_score, _, _ = _keyword_score("가계부 만들어줘 지출 관리")
        assert best_t2 == "budget"
        assert t2_score >= 2


class TestRouteSkill:
    @pytest.mark.asyncio
    async def test_high_confidence_keyword(self):
        result = await route_skill("운동 기록 일지 헬스 트래커")
        assert result.skill_id == "fitness"
        assert result.method == "keyword"
        assert result.confidence >= 0.5

    @pytest.mark.asyncio
    async def test_ambiguous_calls_llm(self):
        mock_provider = AsyncMock()
        mock_provider.call = AsyncMock(
            return_value={
                "skill_id": "diary",
                "confidence": 0.85,
                "reasoning": "일상 기록 요청",
            }
        )
        result = await route_skill("내 일상을 정리해보고 싶어", provider=mock_provider)
        assert result.skill_id == "diary"
        assert result.method == "llm"
        mock_provider.call.assert_called_once()

    @pytest.mark.asyncio
    async def test_llm_low_confidence_falls_through(self):
        mock_provider = AsyncMock()
        mock_provider.call = AsyncMock(
            return_value={
                "skill_id": "track",
                "confidence": 0.1,
            }
        )
        result = await route_skill("뭔가 만들어줘", provider=mock_provider)
        assert result.skill_id is None or result.confidence <= 0.3

    @pytest.mark.asyncio
    async def test_no_provider_weak_keyword(self):
        result = await route_skill("습관")
        assert result.method in ("keyword_weak", "keyword")

    @pytest.mark.asyncio
    async def test_completely_unmatched(self):
        result = await route_skill("xyz 아무것도 아닌 것")
        assert result.skill_id is None
        assert result.method == "none"

    @pytest.mark.asyncio
    async def test_llm_error_graceful(self):
        mock_provider = AsyncMock()
        mock_provider.call = AsyncMock(side_effect=RuntimeError("API 오류"))
        result = await route_skill("독서 기록", provider=mock_provider)
        assert result is not None


class TestBuildSkillGuide:
    @pytest.mark.asyncio
    async def test_matched_skill_in_guide(self):
        guide, match = await build_skill_guide("운동 기록 일지 헬스 트래커")
        assert match.skill_id == "fitness"
        assert "MATCHED SKILL" in guide

    @pytest.mark.asyncio
    async def test_no_message_returns_full_list(self):
        guide, match = await build_skill_guide("")
        assert match.skill_id is None
        assert "Available Skills" in guide

    @pytest.mark.asyncio
    async def test_available_skills_listed(self):
        guide, _ = await build_skill_guide("프로젝트 관리 보드 태스크")
        assert "Available Skills" in guide


class TestExtractSkillEssentials:
    def test_extracts_required_properties(self):
        skill_md = """---
name: test
---

Some intro

### Required Properties
- 이름: title
- 날짜: date

## Other Section
Extra content
"""
        result = _extract_skill_essentials(skill_md)
        assert "Required Properties" in result
        assert "이름" in result

    def test_short_skill_returns_content(self):
        skill_md = "line1\nline2\nline3\nline4\nline5\nline6\nline7\nline8"
        result = _extract_skill_essentials(skill_md)
        assert "line5" in result


class TestSkillMatchDataclass:
    def test_frozen(self):
        match = SkillMatch(skill_id="fitness", confidence=0.9, method="keyword")
        with pytest.raises(AttributeError):
            match.skill_id = "other"

    def test_none_skill(self):
        match = SkillMatch(skill_id=None, confidence=0.0, method="none")
        assert match.skill_id is None
