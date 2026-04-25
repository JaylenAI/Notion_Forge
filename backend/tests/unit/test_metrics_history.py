"""Metrics + History 테스트"""

import time

from app.core.history import get_recent_history, save_generation_record
from app.core.metrics import GenerationMetrics, StageMetric


class TestStageMetric:
    def test_duration_ms(self):
        s = StageMetric(name="test", start_time=1000.0, end_time=1000.5)
        assert s.duration_ms == 500

    def test_duration_zero_when_not_finished(self):
        s = StageMetric(name="test", start_time=1000.0)
        assert s.duration_ms == 0


class TestGenerationMetrics:
    def test_basic_lifecycle(self):
        m = GenerationMetrics(session_id="t1", user_input="test")
        m.start_stage("intent")
        time.sleep(0.01)
        m.end_stage()
        m.start_stage("gen")
        time.sleep(0.01)
        m.end_stage()
        m.blocks_count = 10
        m.databases_count = 2
        m.finish(success=True)

        assert m.success
        assert m.total_duration_ms > 0
        assert len(m.stages) == 2
        assert m.stages[0].name == "intent"
        assert m.stages[1].name == "gen"

    def test_to_dict(self):
        m = GenerationMetrics(session_id="t2", user_input="hello world", skill="fitness", complexity="simple")
        m.finish(success=True)
        d = m.to_dict()

        assert d["session_id"] == "t2"
        assert d["skill"] == "fitness"
        assert d["complexity"] == "simple"
        assert d["success"] is True
        assert isinstance(d["stages"], list)
        assert d["total_duration_ms"] >= 0

    def test_failure(self):
        m = GenerationMetrics(session_id="t3", user_input="fail")
        m.finish(success=False, error="timeout")
        assert not m.success
        assert m.error == "timeout"

    def test_truncate_user_input(self):
        m = GenerationMetrics(session_id="t4", user_input="x" * 500)
        d = m.to_dict()
        assert len(d["user_input"]) == 200


class TestHistory:
    def test_save_and_retrieve(self):
        metrics_dict = {"session_id": "hist_test", "success": True, "skill": "test"}
        result = save_generation_record(
            metrics_dict, {"metadata": {"title": "Test Template", "template_type": "track"}}
        )
        assert result is not None

        records = get_recent_history(days=1, limit=100)
        assert any(r.get("metrics", {}).get("session_id") == "hist_test" for r in records)

    def test_blueprint_meta_stored(self):
        bp = {
            "metadata": {
                "title": "My Template",
                "template_type": "fitness",
                "color_theme": "orange",
                "skill_used": "fitness",
                "generation_method": "ai_dynamic",
            },
            "blocks": [{"type": "callout"}] * 5,
            "databases": [{"title": "DB1"}],
            "sub_pages": [],
        }
        save_generation_record({"session_id": "meta_test"}, bp)
        records = get_recent_history(days=1, limit=100)
        meta_rec = next((r for r in records if r.get("metrics", {}).get("session_id") == "meta_test"), None)
        assert meta_rec is not None
        assert meta_rec["blueprint_meta"]["title"] == "My Template"
        assert meta_rec["blueprint_meta"]["blocks_count"] == 5
