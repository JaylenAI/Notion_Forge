"""judge→repair 루프 테스트 (Phase 1) — judge/생성 주입으로 네트워크 없이 검증."""

import copy

import app.agent.blueprint_generator as bg
from app.agent.premium_judge import JudgeVerdict

_PASS = JudgeVerdict(
    overall_pass=True,
    estimated_band="$20-49",
    verdicts=[{"criterion": c, "pass": True} for c in ("domain_fit", "naming", "layout", "completeness", "wtp")],
    pass_count=5,
    total=5,
)


def _fail():
    return JudgeVerdict(
        overall_pass=False,
        estimated_band="$5-15",
        verdicts=[
            {"criterion": "domain_fit", "pass": True},
            {"criterion": "completeness", "pass": False},
            {"criterion": "wtp", "pass": False},
        ],
        pass_count=1,
        total=3,
    )


class _JudgeSeq:
    """호출 순서대로 verdict 반환 (1차=초기심사, 2차=재심사)."""

    def __init__(self, seq):
        self.seq = seq
        self.i = 0
        self.calls = 0

    async def __call__(self, blueprint, ai_key="", ai_model="", provider=None, timeout=30.0):
        self.calls += 1
        v = self.seq[min(self.i, len(self.seq) - 1)]
        self.i += 1
        return v


# 재생성이 내놓는 풍부한 멀티DB 콘텐츠 (assemble+enrich 시 고득점)
_RICH = {
    "title": "CRM",
    "color": "blue",
    "blocks": [
        {"type": "callout", "text": "환영"},
        {"type": "heading_1", "text": "딜"},
        {"type": "database_ref", "db_index": 0},
        {"type": "database_ref", "db_index": 1},
    ],
    "databases": [
        {
            "title": "고객",
            "db_properties": {
                "고객명": "title",
                "총딜": {"type": "rollup", "relation_property": "딜"},
                "딜": {"type": "relation", "target_db_index": 1},
            },
            "views": [{"type": "table"}],
            "sample_items": [{"고객명": "A"}, {"고객명": "B"}, {"고객명": "C"}],
        },
        {
            "title": "딜",
            "db_properties": {"딜명": "title", "금액": "number", "고객": {"type": "relation", "target_db_index": 0}},
            "views": [{"type": "board"}],
            "sample_items": [{"딜명": "d1", "고객": "A"}, {"딜명": "d2", "고객": "B"}, {"딜명": "d3", "고객": "C"}],
        },
    ],
    "sub_pages": [{"name": "시작하기", "blocks": []}],
}


def _original(score: float) -> dict:
    return {
        "metadata": {"title": "X", "premium_score": score, "premium_weakest": ["relation_rollup"]},
        "main_page": {"title": "X"},
        "blocks": [{"type": "callout", "text": "x"}],
        "databases": [{"title": "DB", "properties": {"이름": "title"}}],
        "sub_pages": [],
    }


async def test_judge_pass_no_repair(monkeypatch):
    j = _JudgeSeq([_PASS])
    monkeypatch.setattr("app.agent.premium_judge.judge_blueprint", j)
    called = {"n": 0}

    async def no_call(*a, **k):
        called["n"] += 1
        return None

    monkeypatch.setattr(bg, "_call_ai_for_content", no_call)

    bp = _original(80)
    out = await bg._finalize_blueprint(bp, "msg", "", "")
    assert out is bp
    assert bp["metadata"]["judge_pass"] is True
    assert called["n"] == 0  # 재생성 미발생


async def test_judge_none_returns_original(monkeypatch):
    async def jnone(*a, **k):
        return None

    monkeypatch.setattr("app.agent.premium_judge.judge_blueprint", jnone)
    bp = _original(50)
    out = await bg._finalize_blueprint(bp, "msg", "", "")
    assert out is bp
    assert "judge_pass" not in bp["metadata"]


async def test_repair_disabled_no_regen(monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "judge_repair_enabled", False)
    monkeypatch.setattr("app.agent.premium_judge.judge_blueprint", _JudgeSeq([_fail()]))
    called = {"n": 0}

    async def no_call(*a, **k):
        called["n"] += 1
        return None

    monkeypatch.setattr(bg, "_call_ai_for_content", no_call)

    bp = _original(50)
    out = await bg._finalize_blueprint(bp, "msg", "", "")
    assert out is bp
    assert bp["metadata"]["judge_pass"] is False
    assert called["n"] == 0


async def test_repair_adopts_better(monkeypatch):
    monkeypatch.setattr("app.agent.premium_judge.judge_blueprint", _JudgeSeq([_fail(), _PASS]))

    async def rich_call(*a, **k):
        return copy.deepcopy(_RICH)

    monkeypatch.setattr(bg, "_call_ai_for_content", rich_call)

    bp = _original(30)  # 낮음 → 재생성이 이김
    out = await bg._finalize_blueprint(bp, "고객 CRM 만들어줘", "", "")
    assert out is not bp
    assert out["metadata"].get("judge_repaired") is True
    assert out["metadata"]["premium_score"] > 30


async def test_repair_keeps_original_when_worse(monkeypatch):
    monkeypatch.setattr("app.agent.premium_judge.judge_blueprint", _JudgeSeq([_fail(), _fail()]))

    async def rich_call(*a, **k):
        return copy.deepcopy(_RICH)

    monkeypatch.setattr(bg, "_call_ai_for_content", rich_call)

    bp = _original(99)  # 매우 높음 → 재생성이 못 이김 → 원본 유지
    out = await bg._finalize_blueprint(bp, "msg", "", "")
    assert out is bp
