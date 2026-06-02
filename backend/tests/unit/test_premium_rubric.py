"""PremiumRubric 단위 + 실데이터(golden) 검증 (Phase A1)."""

import json
from pathlib import Path

import pytest

from app.agent.blueprint_generator import _assemble_blueprint
from app.agent.premium_rubric import PremiumRubricResult, score_blueprint

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "app/agent/prompts/golden"


def _bare_blueprint() -> dict:
    """1개 빈약한 DB + 환영 callout만 — 판매 불가 수준."""
    return {
        "metadata": {"title": "메모", "color_theme": "default"},
        "main_page": {"title": "메모", "icon": "", "cover_url": ""},
        "blocks": [
            {"type": "callout", "text": "환영합니다"},
            {"type": "database_ref", "db_index": 0},
        ],
        "databases": [
            {
                "title": "목록",
                "properties": {"이름": "title", "메모": "rich_text"},
                "views": [{"type": "table"}],
                "sample_items": [],
            }
        ],
        "sub_pages": [],
    }


def _connected_blueprint(with_sample_links: bool) -> dict:
    """2 DB relation+rollup. 샘플 링크 유무로 working-rollup 점수 차이를 검증."""
    deals = [{"딜명": f"딜{i}", "고객": "고객A" if with_sample_links else ""} for i in range(5)]
    return {
        "metadata": {"title": "CRM", "color_theme": "blue"},
        "main_page": {"title": "CRM", "icon": "📊", "cover_url": "http://x/cover.jpg"},
        "blocks": [
            {"type": "callout", "text": "환영"},
            {"type": "heading_1", "text": "딜"},
            {"type": "column_list", "columns": []},
            {"type": "database_ref", "db_index": 0},
            {"type": "database_ref", "db_index": 1},
        ],
        "databases": [
            {
                "title": "고객",
                "properties": {
                    "고객명": "title",
                    "총딜금액": {
                        "type": "rollup",
                        "relation_property": "딜",
                        "rollup_property": "금액",
                        "function": "sum",
                    },
                    "딜": {"type": "relation", "target_db_index": 1},
                },
                "views": [{"type": "table"}],
                "sample_items": [{"고객명": "고객A"}, {"고객명": "고객B"}, {"고객명": "고객C"}],
            },
            {
                "title": "딜",
                "properties": {
                    "딜명": "title",
                    "금액": "number",
                    "고객": {"type": "relation", "target_db_index": 0},
                },
                "views": [{"type": "board", "group_by": {"property": "상태"}}],
                "sample_items": deals,
            },
        ],
        "sub_pages": [{"title": "시작하기 가이드", "icon": "📖", "description": "사용 방법 안내"}],
    }


def test_score_returns_normalized_result():
    r = score_blueprint(_bare_blueprint())
    assert isinstance(r, PremiumRubricResult)
    assert 0.0 <= r.score <= 100.0
    # video/support는 산출물 밖 → applicable=False
    na = [c for c in r.criteria if not c.applicable]
    assert {c.key for c in na} == {"video", "support"}


def test_bare_blueprint_not_sellable():
    r = score_blueprint(_bare_blueprint())
    assert r.score < 60, f"빈약한 템플릿이 판매급으로 잘못 채점됨: {r.score}"
    weak_keys = {c.key for c in r.weakest(4)}
    # 빈약한 템플릿의 핵심 결손: 관계/집계, 온보딩
    assert "relation_rollup" in weak_keys
    assert "onboarding" in weak_keys


def test_connected_blueprint_scores_higher_than_bare():
    bare = score_blueprint(_bare_blueprint())
    connected = score_blueprint(_connected_blueprint(with_sample_links=True))
    assert connected.score > bare.score + 20


def test_working_rollup_requires_sample_links():
    """샘플행이 relation을 채워야 rollup이 집계 가능 → 점수 차이."""
    linked = score_blueprint(_connected_blueprint(with_sample_links=True))
    unlinked = score_blueprint(_connected_blueprint(with_sample_links=False))
    rr_linked = next(c for c in linked.criteria if c.key == "relation_rollup")
    rr_unlinked = next(c for c in unlinked.criteria if c.key == "relation_rollup")
    assert rr_linked.score > rr_unlinked.score


def test_onboarding_detected_from_subpage():
    r = score_blueprint(_connected_blueprint(with_sample_links=True))
    onboarding = next(c for c in r.criteria if c.key == "onboarding")
    assert onboarding.score == 1.0


def test_to_metadata_shape():
    r = score_blueprint(_connected_blueprint(with_sample_links=True))
    md = r.to_metadata()
    assert set(md) >= {"premium_score", "premium_band", "premium_band_label", "premium_weakest"}
    assert isinstance(md["premium_weakest"], list)


@pytest.mark.parametrize("golden_file", sorted(GOLDEN_DIR.glob("*.json")))
def test_golden_templates_score_reasonably(golden_file):
    """실데이터: 8개 golden 레이아웃을 조립→채점. 구조적 최저선을 넘는지 회귀 가드."""
    content = json.loads(golden_file.read_text(encoding="utf-8"))
    blueprint = _assemble_blueprint(content, content.get("title", "테스트"))
    r = score_blueprint(blueprint)
    # golden은 정성껏 만든 예시 — 최소한 '심플' 밴드($5-15, 40점) 이상은 나와야 한다
    assert r.score >= 40, f"{golden_file.name}: 예상보다 낮은 점수 {r.score} ({r.band_price})"


def test_multidb_golden_is_sellable():
    """실데이터: 멀티DB 플래그십(dashboard_widgets)은 $20-49 이상이어야 한다."""
    content = json.loads((GOLDEN_DIR / "dashboard_widgets.json").read_text(encoding="utf-8"))
    blueprint = _assemble_blueprint(content, "CRM 대시보드")
    r = score_blueprint(blueprint)
    assert r.score >= 60, f"멀티DB 골든이 판매급 미달: {r.score} ({r.band_price})"
