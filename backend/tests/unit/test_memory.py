"""Episodic Memory 단위 테스트"""

import pytest
from pathlib import Path
from datetime import datetime, timezone

from app.agent.memory import EpisodicMemory, Episode


@pytest.fixture
def memory(tmp_path):
    return EpisodicMemory(memory_dir=tmp_path / "memory")


class TestEpisodeStorage:
    def test_save_and_retrieve(self, memory):
        episode = Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_message="운동 기록 만들어줘",
            skill_used="fitness",
            layout="simple_tracker",
            success=True,
            gen_eval_attempts=1,
        )
        memory.save_episode(episode)
        episodes = memory.get_recent_episodes(limit=5)
        assert len(episodes) == 1
        assert episodes[0].skill_used == "fitness"
        assert episodes[0].success is True

    def test_multiple_episodes_order(self, memory):
        for i in range(5):
            memory.save_episode(Episode(
                timestamp=f"2026-04-{20+i}T00:00:00Z",
                user_message=f"test {i}",
                skill_used=f"skill_{i}",
                layout="simple_tracker",
                success=True,
            ))
        episodes = memory.get_recent_episodes(limit=3)
        assert len(episodes) == 3
        assert episodes[0].user_message == "test 4"

    def test_similar_episodes(self, memory):
        for skill in ["fitness", "reading", "fitness", "project", "fitness"]:
            memory.save_episode(Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message=f"{skill} test",
                skill_used=skill,
                layout="simple_tracker",
                success=True,
            ))
        similar = memory.get_similar_episodes("fitness")
        assert len(similar) == 3
        assert all(ep.skill_used == "fitness" for ep in similar)

    def test_empty_memory(self, memory):
        assert memory.get_recent_episodes() == []
        assert memory.get_similar_episodes("fitness") == []


class TestPreferences:
    def test_save_and_get(self, memory):
        memory.save_preference("color_theme", "blue")
        assert memory.get_preference("color_theme") == "blue"

    def test_default_value(self, memory):
        assert memory.get_preference("missing", "default") == "default"

    def test_overwrite(self, memory):
        memory.save_preference("lang", "ko")
        memory.save_preference("lang", "en")
        assert memory.get_preference("lang") == "en"

    def test_get_all(self, memory):
        memory.save_preference("a", "1")
        memory.save_preference("b", "2")
        prefs = memory.get_all_preferences()
        assert prefs == {"a": "1", "b": "2"}


class TestSkillStats:
    def test_stats_updated_on_save(self, memory):
        memory.save_episode(Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_message="test",
            skill_used="fitness",
            layout="simple_tracker",
            success=True,
            gen_eval_attempts=2,
        ))
        stats = memory.get_skill_stats()
        assert "fitness" in stats
        assert stats["fitness"]["total"] == 1
        assert stats["fitness"]["success"] == 1
        assert stats["fitness"]["avg_attempts"] == 2.0

    def test_stats_accumulate(self, memory):
        for success in [True, True, False]:
            memory.save_episode(Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test",
                skill_used="project",
                layout="kanban_board",
                success=success,
                gen_eval_attempts=1,
            ))
        stats = memory.get_skill_stats()
        assert stats["project"]["total"] == 3
        assert stats["project"]["success"] == 2
        assert stats["project"]["fail"] == 1

    def test_empty_stats(self, memory):
        assert memory.get_skill_stats() == {}


class TestMemoryContext:
    def test_context_with_preferences(self, memory):
        memory.save_preference("color_theme", "blue")
        context = memory.build_memory_context()
        assert "User Preferences" in context
        assert "blue" in context

    def test_context_with_episodes(self, memory):
        memory.save_episode(Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_message="운동",
            skill_used="fitness",
            layout="simple_tracker",
            success=True,
            gen_eval_attempts=1,
        ))
        context = memory.build_memory_context(skill="fitness")
        assert "fitness" in context

    def test_empty_context(self, memory):
        context = memory.build_memory_context()
        assert context == ""

    def test_context_includes_stats(self, memory):
        memory.save_episode(Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_message="test",
            skill_used="reading",
            layout="gallery_hero",
            success=True,
        ))
        context = memory.build_memory_context(skill="reading")
        assert "success rate" in context


class TestClear:
    def test_clear_removes_all(self, memory):
        memory.save_preference("key", "val")
        memory.save_episode(Episode(
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_message="test",
            skill_used="test",
            layout="test",
            success=True,
        ))
        memory.clear()
        assert memory.get_all_preferences() == {}
        assert memory.get_recent_episodes() == []
        assert memory.get_skill_stats() == {}
