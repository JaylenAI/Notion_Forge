"""SkillMatcher 테스트: 스킬 매칭 + 가이드 빌드 검증"""

from app.agent.skill_matcher import (
    TIER2_SKILLS,
    _extract_skill_essentials,
    _match_specific_skill,
    build_skill_guide,
)


class TestExtractSkillEssentials:
    def test_captures_required_properties(self):
        md = "## Overview\nSome text\n### Required Properties\n- 이름: title\n- 상태: status\n## Other\nMore"
        result = _extract_skill_essentials(md)
        assert "이름" in result
        assert "상태" in result

    def test_captures_views_section(self):
        md = "## Overview\nSome text\n### Views\n- board\n- calendar\n## Other"
        result = _extract_skill_essentials(md)
        assert "board" in result

    def test_max_12_lines(self):
        md = "## Overview\n### Required Properties\n" + "\n".join(f"line{i}" for i in range(30))
        result = _extract_skill_essentials(md)
        assert len(result.split("\n")) <= 13

    def test_fallback_when_no_keywords(self):
        md = "line1\nline2\nline3\nline4\nfallback5\nfallback6\nfallback7\nfallback8\nfallback9"
        result = _extract_skill_essentials(md)
        assert "fallback5" in result


class TestMatchSpecificSkill:
    def test_matches_tier2_by_keyword(self):
        result = _match_specific_skill("프로젝트 관리 템플릿 만들어줘")
        assert result is not None

    def test_no_match_for_gibberish(self):
        result = _match_specific_skill("xyzzy foobar bazzle")
        assert result is None

    def test_tier2_skills_exist(self):
        assert "project" in TIER2_SKILLS
        assert "fitness" in TIER2_SKILLS
        assert "budget" in TIER2_SKILLS


class TestBuildSkillGuide:
    def test_returns_string(self):
        result = build_skill_guide("프로젝트 관리")
        assert isinstance(result, str)
        assert "Available Skills" in result

    def test_empty_message(self):
        result = build_skill_guide("")
        assert "Available Skills" in result

    def test_matched_skill_prioritized(self):
        result = build_skill_guide("운동 루틴 트래커 만들어줘")
        if "MATCHED SKILL" in result:
            assert "FOLLOW THIS SKILL" in result
