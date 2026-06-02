"""QualityReport 통합 단위 테스트 (Phase A1)."""

from app.agent.quality_report import (
    attach_deterministic_quality,
    attach_full_quality,
    build_deterministic_report,
)


def _blueprint():
    return {
        "metadata": {"title": "CRM", "color_theme": "blue"},
        "main_page": {"title": "CRM", "icon": "📊", "cover_url": "http://x/c.jpg"},
        "blocks": [
            {"type": "callout", "text": "환영"},
            {"type": "heading_1", "text": "딜"},
            {"type": "database_ref", "db_index": 0},
            {"type": "database_ref", "db_index": 1},
        ],
        "databases": [
            {
                "title": "고객",
                "properties": {"고객명": "title", "딜": {"type": "relation", "target_db_index": 1}},
                "views": [{"type": "table"}],
                "sample_items": [{"고객명": "A"}, {"고객명": "B"}, {"고객명": "C"}],
            },
            {
                "title": "딜",
                "properties": {"딜명": "title", "금액": "number", "고객": {"type": "relation", "target_db_index": 0}},
                "views": [{"type": "board"}],
                "sample_items": [
                    {"딜명": "딜1", "고객": "A"},
                    {"딜명": "딜2", "고객": "B"},
                    {"딜명": "딜3", "고객": "C"},
                ],
            },
        ],
        "sub_pages": [{"title": "시작하기 가이드", "icon": "📖"}],
    }


class _FakeProvider:
    name = "fake"

    async def call_with_retry(self, system, user, model="", timeout=30.0):
        return {
            "verdicts": [
                {"criterion": c, "pass": True, "reason": "x"}
                for c in ("domain_fit", "naming_quality", "layout_sense", "completeness", "willingness_to_pay")
            ],
            "overall_pass": True,
            "estimated_band": "$20-49",
        }


def test_build_deterministic_report():
    rep = build_deterministic_report(_blueprint())
    assert rep.structural_score >= 0
    assert 0 <= rep.premium.score <= 100
    assert rep.structural_breakdown is not None
    assert rep.judge is None


def test_attach_deterministic_mutates_metadata():
    bp = _blueprint()
    attach_deterministic_quality(bp)
    md = bp["metadata"]
    assert "quality_score" in md
    assert "premium_score" in md
    assert "premium_band" in md
    assert "quality_breakdown" in md
    # 기존 필드명 호환 유지 (다운스트림이 quality_score 사용)
    assert isinstance(md["quality_score"], (int, float))


async def test_attach_full_quality_with_judge():
    bp = _blueprint()
    rep = await attach_full_quality(bp, enable_judge=True, provider=_FakeProvider())
    assert rep.judge is not None
    assert bp["metadata"]["judge_pass"] is True
    assert bp["metadata"]["premium_score"] == rep.premium.score


async def test_attach_full_quality_judge_disabled():
    bp = _blueprint()
    rep = await attach_full_quality(bp, enable_judge=False, provider=_FakeProvider())
    assert rep.judge is None
    assert "judge_pass" not in bp["metadata"]
    # 결정적 신호는 여전히 부착됨
    assert "premium_score" in bp["metadata"]
