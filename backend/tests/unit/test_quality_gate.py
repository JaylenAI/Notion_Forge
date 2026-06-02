"""품질 게이트 + blueprint pin 테스트 (Phase A4)."""

from app.agent.premium_rubric import CriterionScore, PremiumRubricResult
from app.agent.quality_report import (
    QualityReport,
    attach_deterministic_quality,
    evaluate_premium_gate,
)
from app.core import history


def _report(score: float, passed: bool = True) -> QualityReport:
    pr = PremiumRubricResult(
        score=score,
        band_label="x",
        band_price="$20-49",
        criteria=[
            CriterionScore("linked_db", "연결된 DB 아키텍처", 18, 0.3),
            CriterionScore("onboarding", "온보딩/시작하기", 12, 0.0),
        ],
    )
    return QualityReport(structural_score=80.0, structural_passed=passed, premium=pr)


# ── 게이트 판정 ──


def test_gate_ready_when_above_threshold():
    ready, blockers = evaluate_premium_gate(_report(65), 60)
    assert ready is True and blockers == []


def test_gate_blocks_below_threshold_with_weakness_hint():
    ready, blockers = evaluate_premium_gate(_report(45), 60)
    assert ready is False
    assert any("유료급 점수" in b for b in blockers)
    assert any("약점" in b for b in blockers)  # 개선 가이드 포함


def test_gate_blocks_on_structural_failure():
    ready, blockers = evaluate_premium_gate(_report(70, passed=False), 60)
    assert ready is False
    assert any("구조" in b for b in blockers)


def test_attach_sets_gate_metadata():
    bp = {
        "metadata": {"title": "메모", "color_theme": "default"},
        "main_page": {"title": "메모"},
        "blocks": [{"type": "callout", "text": "환영"}],
        "databases": [
            {"title": "목록", "properties": {"이름": "title"}, "views": [{"type": "table"}], "sample_items": []}
        ],
        "sub_pages": [],
    }
    attach_deterministic_quality(bp)
    md = bp["metadata"]
    assert "premium_ready" in md and isinstance(md["premium_ready"], bool)
    assert "premium_blockers" in md and isinstance(md["premium_blockers"], list)
    # 빈약한 단일DB → 미달이어야 하고 사유가 있어야 함
    assert md["premium_ready"] is False and md["premium_blockers"]


# ── blueprint pin (결정성) ──


def test_pin_round_trip_byte_stable(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "PINNED_DIR", tmp_path / "pinned")
    bp = {
        "metadata": {"title": "고정템플릿"},
        "databases": [{"title": "DB"}],
        "blocks": [{"type": "callout", "text": "x"}],
    }
    path = history.pin_blueprint(bp, "my-template-1")
    assert path is not None and path.exists()
    loaded = history.load_pinned("my-template-1")
    assert loaded == bp  # 동일 → execute_blueprint(결정적)로 동일 재생성 보장

    # 동일 blueprint는 동일 파일 바이트 (byte-stable)
    first_bytes = path.read_bytes()
    history.pin_blueprint(bp, "my-template-1")
    assert path.read_bytes() == first_bytes


def test_pin_missing_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "PINNED_DIR", tmp_path / "pinned")
    assert history.load_pinned("nonexistent") is None


def test_pin_empty_blueprint_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(history, "PINNED_DIR", tmp_path / "pinned")
    assert history.pin_blueprint({}, "x") is None


# ── 회귀: QualityValidator가 조립된 blueprint의 title을 main_page에서 인식 ──
# (top-level title만 보던 결함 → 모든 조립 blueprint가 'title 없음' critical로 오판,
#  게이트가 정상 템플릿을 false-positive로 막던 문제 방지)


def test_validator_recognizes_title_in_main_page():
    from app.agent.quality_validator import QualityValidator

    bp = {
        "main_page": {"title": "프로젝트 관리", "icon": "📋"},
        "metadata": {"color_theme": "blue"},
        "blocks": [{"type": "callout", "text": "환영"}],
        "databases": [{"title": "작업", "properties": {"이름": "title"}, "sample_items": []}],
    }
    r = QualityValidator().validate(bp)
    assert not any("title 필드가 없습니다" in i.message for i in r.issues)
    # 메인 icon이 main_page에 있으면 'icon 누락' 신호도 없어야 함
    assert not any("메인 페이지 icon 누락" in i.message for i in r.issues)
