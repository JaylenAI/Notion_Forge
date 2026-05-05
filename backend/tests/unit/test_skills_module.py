"""Skills 모듈 유닛 테스트 — auto_discover, load, CRUD"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from app.skills import (
    _validate_skill_id,
    auto_discover_skills,
    delete_custom_skill,
    get_custom_skill,
    get_skill_summary,
    get_tool_enum_description,
    load_custom_skills,
    load_skill,
    load_skill_examples,
    save_custom_skill,
)


class TestAutoDiscoverSkills:
    def test_discovers_from_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            skill = skills_dir / "test_skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\ndescription: Test skill\nkeywords: test,demo\n---\n# Content")

            with patch("app.skills.SKILLS_DIR", skills_dir):
                result = auto_discover_skills()
            assert "test_skill" in result
            assert result["test_skill"]["description"] == "Test skill"
            assert "test" in result["test_skill"]["keywords"]

    def test_no_skill_md_skipped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            (skills_dir / "empty_dir").mkdir()

            with patch("app.skills.SKILLS_DIR", skills_dir):
                result = auto_discover_skills()
            assert len(result) == 0


class TestLoadSkill:
    def test_load_builtin(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            skill = skills_dir / "my_skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("# Built-in Content")

            with patch("app.skills.SKILLS_DIR", skills_dir):
                with patch("app.skills.CUSTOM_SKILLS_DIR", Path("/nonexistent")):
                    content = load_skill("my_skill")
            assert content == "# Built-in Content"

    def test_load_custom_priority(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            skill = custom_dir / "my_skill"
            skill.mkdir()
            (skill / "SKILL.md").write_text("# Custom Version")

            with patch("app.skills.CUSTOM_SKILLS_DIR", custom_dir):
                content = load_skill("my_skill")
            assert content == "# Custom Version"

    def test_load_nonexistent(self):
        with patch("app.skills.SKILLS_DIR", Path("/nonexistent")):
            with patch("app.skills.CUSTOM_SKILLS_DIR", Path("/nonexistent")):
                content = load_skill("no_such_skill")
        assert content is None


class TestLoadSkillExamples:
    def test_load_examples(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            examples = skills_dir / "my_skill" / "examples"
            examples.mkdir(parents=True)
            (examples / "01.md").write_text("Example 1")
            (examples / "02.md").write_text("Example 2")

            with patch("app.skills.SKILLS_DIR", skills_dir):
                result = load_skill_examples("my_skill")
            assert len(result) == 2
            assert "Example 1" in result[0]

    def test_no_examples_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            skills_dir = Path(tmpdir)
            (skills_dir / "my_skill").mkdir()

            with patch("app.skills.SKILLS_DIR", skills_dir):
                result = load_skill_examples("my_skill")
            assert result == []


class TestGetSkillSummary:
    def test_returns_string(self):
        summary = get_skill_summary()
        assert isinstance(summary, str)
        assert len(summary) > 0


class TestGetToolEnumDescription:
    def test_returns_string(self):
        desc = get_tool_enum_description()
        assert isinstance(desc, str)
        assert "=" in desc


class TestValidateSkillId:
    def test_valid(self):
        assert _validate_skill_id("my_skill") is True
        assert _validate_skill_id("a") is True
        assert _validate_skill_id("skill_123") is True

    def test_invalid_empty(self):
        assert _validate_skill_id("") is False

    def test_invalid_uppercase(self):
        assert _validate_skill_id("MySkill") is False

    def test_invalid_traversal(self):
        assert _validate_skill_id("../etc") is False

    def test_invalid_slash(self):
        assert _validate_skill_id("path/to") is False


class TestCustomSkillCRUD:
    def test_save_and_get(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.skills.CUSTOM_SKILLS_DIR", Path(tmpdir)):
                save_custom_skill("test_skill", "# Content")
                result = get_custom_skill("test_skill")
        assert result is not None
        assert result["content"] == "# Content"

    def test_save_invalid_id(self):
        with pytest.raises(ValueError, match="Invalid skill ID"):
            save_custom_skill("../bad", "content")

    def test_delete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            skill_dir = custom_dir / "to_delete"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text("content")

            with patch("app.skills.CUSTOM_SKILLS_DIR", custom_dir):
                result = delete_custom_skill("to_delete")
            assert result is True
            assert not skill_dir.exists()

    def test_delete_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.skills.CUSTOM_SKILLS_DIR", Path(tmpdir)):
                result = delete_custom_skill("nope")
        assert result is False

    def test_delete_invalid_id(self):
        with pytest.raises(ValueError):
            delete_custom_skill("../bad")

    def test_get_nonexistent(self):
        with patch("app.skills.CUSTOM_SKILLS_DIR", Path("/nonexistent")):
            result = get_custom_skill("nope")
        assert result is None


class TestLoadCustomSkills:
    def test_loads_from_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_dir = Path(tmpdir)
            skill = custom_dir / "my_custom"
            skill.mkdir()
            (skill / "SKILL.md").write_text("---\ndescription: Custom desc\nkeywords: custom,test\n---\n# Body")

            with patch("app.skills.CUSTOM_SKILLS_DIR", custom_dir):
                result = load_custom_skills()
            assert "my_custom" in result
            assert result["my_custom"]["description"] == "Custom desc"

    def test_empty_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("app.skills.CUSTOM_SKILLS_DIR", Path(tmpdir)):
                result = load_custom_skills()
            assert result == {}

    def test_nonexistent_dir(self):
        with patch("app.skills.CUSTOM_SKILLS_DIR", Path("/nonexistent")):
            result = load_custom_skills()
        assert result == {}
