"""Episodic Memory 단위 테스트"""

from datetime import datetime, timezone

import pytest

from app.agent.memory import Episode, EpisodicMemory, _keyword_similarity, _tokenize


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
            memory.save_episode(
                Episode(
                    timestamp=f"2026-04-{20 + i}T00:00:00Z",
                    user_message=f"test {i}",
                    skill_used=f"skill_{i}",
                    layout="simple_tracker",
                    success=True,
                )
            )
        episodes = memory.get_recent_episodes(limit=3)
        assert len(episodes) == 3
        assert episodes[0].user_message == "test 4"

    def test_similar_episodes(self, memory):
        for skill in ["fitness", "reading", "fitness", "project", "fitness"]:
            memory.save_episode(
                Episode(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    user_message=f"{skill} test",
                    skill_used=skill,
                    layout="simple_tracker",
                    success=True,
                )
            )
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
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test",
                skill_used="fitness",
                layout="simple_tracker",
                success=True,
                gen_eval_attempts=2,
            )
        )
        stats = memory.get_skill_stats()
        assert "fitness" in stats
        assert stats["fitness"]["total"] == 1
        assert stats["fitness"]["success"] == 1
        assert stats["fitness"]["avg_attempts"] == 2.0

    def test_stats_accumulate(self, memory):
        for success in [True, True, False]:
            memory.save_episode(
                Episode(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    user_message="test",
                    skill_used="project",
                    layout="kanban_board",
                    success=success,
                    gen_eval_attempts=1,
                )
            )
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
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="운동",
                skill_used="fitness",
                layout="simple_tracker",
                success=True,
                gen_eval_attempts=1,
            )
        )
        context = memory.build_memory_context(skill="fitness")
        assert "fitness" in context

    def test_empty_context(self, memory):
        context = memory.build_memory_context()
        assert context == ""

    def test_context_includes_stats(self, memory):
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test",
                skill_used="reading",
                layout="gallery_hero",
                success=True,
            )
        )
        context = memory.build_memory_context(skill="reading")
        assert "success rate" in context


class TestTokenize:
    def test_korean_tokens(self):
        tokens = _tokenize("운동 기록 만들어줘")
        assert "운동" in tokens
        assert "기록" in tokens
        assert "만들어줘" not in tokens

    def test_english_tokens(self):
        tokens = _tokenize("project management dashboard")
        assert "project" in tokens
        assert "management" in tokens
        assert "dashboard" in tokens

    def test_stop_words_removed(self):
        tokens = _tokenize("나의 독서 기록 만들어줘")
        assert "독서" in tokens
        assert "기록" in tokens
        assert "만들어줘" not in tokens

    def test_single_char_removed(self):
        tokens = _tokenize("a b 가 나다")
        assert "나다" in tokens
        assert "가" not in tokens


class TestKeywordSimilarity:
    def test_exact_match(self):
        score = _keyword_similarity(["운동", "기록"], ["운동", "기록"])
        assert score == 1.0

    def test_partial_match(self):
        score = _keyword_similarity(["운동", "기록"], ["운동", "트래커"])
        assert 0.0 < score < 1.0

    def test_no_match(self):
        score = _keyword_similarity(["운동", "기록"], ["독서", "감상"])
        assert score == 0.0

    def test_substring_match(self):
        score = _keyword_similarity(["프로젝트"], ["프로젝트관리"])
        assert score > 0.0

    def test_empty_input(self):
        assert _keyword_similarity([], ["운동"]) == 0.0
        assert _keyword_similarity(["운동"], []) == 0.0


class TestSemanticSearch:
    def test_query_based_similarity(self, memory):
        memory.save_episode(
            Episode(
                timestamp="2026-04-20T00:00:00Z",
                user_message="운동 기록 트래커",
                skill_used="fitness",
                layout="simple_tracker",
                success=True,
            )
        )
        memory.save_episode(
            Episode(
                timestamp="2026-04-21T00:00:00Z",
                user_message="독서 감상 기록",
                skill_used="reading",
                layout="gallery_hero",
                success=True,
            )
        )
        memory.save_episode(
            Episode(
                timestamp="2026-04-22T00:00:00Z",
                user_message="운동 루틴 관리",
                skill_used="fitness",
                layout="kanban_board",
                success=True,
            )
        )
        results = memory.get_similar_episodes("fitness", query="운동 루틴")
        assert len(results) >= 1
        assert results[0].user_message == "운동 루틴 관리"

    def test_cross_skill_similarity(self, memory):
        memory.save_episode(
            Episode(
                timestamp="2026-04-20T00:00:00Z",
                user_message="프로젝트 관리 대시보드",
                skill_used="project",
                layout="dashboard",
                success=True,
            )
        )
        results = memory.get_similar_episodes("custom", query="프로젝트 관리")
        assert len(results) >= 1

    def test_no_query_falls_back_to_skill_match(self, memory):
        memory.save_episode(
            Episode(
                timestamp="2026-04-20T00:00:00Z",
                user_message="test",
                skill_used="fitness",
                layout="simple",
                success=True,
            )
        )
        results = memory.get_similar_episodes("fitness")
        assert len(results) == 1
        assert results[0].skill_used == "fitness"


class TestSkillSuccessPatterns:
    def test_patterns_analysis(self, memory):
        for layout, success in [("simple", True), ("kanban", True), ("simple", True), ("dashboard", False)]:
            memory.save_episode(
                Episode(
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    user_message="test",
                    skill_used="fitness",
                    layout=layout,
                    success=success,
                    error_types=["gen_eval_exhausted"] if not success else [],
                )
            )
        patterns = memory.get_skill_success_patterns("fitness")
        assert patterns["total"] == 4
        assert patterns["success_count"] == 3
        assert patterns["fail_count"] == 1
        assert patterns["best_layouts"][0][0] == "simple"
        assert patterns["common_errors"][0][0] == "gen_eval_exhausted"

    def test_empty_patterns(self, memory):
        patterns = memory.get_skill_success_patterns("nonexistent")
        assert patterns == {}


class TestCache:
    def test_cache_reuses_on_same_mtime(self, memory):
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test",
                skill_used="test",
                layout="test",
                success=True,
            )
        )
        eps1 = memory._load_episodes_cached()
        eps2 = memory._load_episodes_cached()
        assert eps1 is eps2

    def test_cache_invalidated_on_save(self, memory):
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test",
                skill_used="test",
                layout="test",
                success=True,
            )
        )
        eps1 = memory._load_episodes_cached()
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test2",
                skill_used="test2",
                layout="test",
                success=True,
            )
        )
        eps2 = memory._load_episodes_cached()
        assert len(eps2) == 2
        assert eps1 is not eps2


class TestClear:
    def test_clear_removes_all(self, memory):
        memory.save_preference("key", "val")
        memory.save_episode(
            Episode(
                timestamp=datetime.now(timezone.utc).isoformat(),
                user_message="test",
                skill_used="test",
                layout="test",
                success=True,
            )
        )
        memory.clear()
        assert memory.get_all_preferences() == {}
        assert memory.get_recent_episodes() == []
        assert memory.get_skill_stats() == {}
