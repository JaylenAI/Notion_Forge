"""Sellability 보강 단위 테스트 (Phase A2) — 보강이 루브릭 점수를 올리는지 검증."""

from app.agent.premium_rubric import score_blueprint
from app.agent.sellability import (
    enrich_blueprint,
    ensure_toc,
    inject_onboarding_page,
    inject_top_nav,
)


def _blueprint(sub_pages=None):
    return {
        "metadata": {"title": "프로젝트 관리", "color_theme": "blue"},
        "main_page": {"title": "프로젝트 관리", "icon": "📋", "cover_url": "http://x/c.jpg"},
        "blocks": [
            {"type": "callout", "text": "환영"},
            {"type": "heading_1", "text": "프로젝트"},
            {"type": "database_ref", "db_index": 0},
        ],
        "databases": [
            {
                "title": "프로젝트",
                "properties": {"이름": "title", "상태": "status"},
                "views": [{"type": "board"}, {"type": "table"}],
                "sample_items": [{"이름": "A"}, {"이름": "B"}, {"이름": "C"}],
                "description": "프로젝트 추적",
            }
        ],
        "sub_pages": sub_pages if sub_pages is not None else [],
    }


def test_inject_onboarding_adds_guide_subpage():
    bp = _blueprint()
    added = inject_onboarding_page(bp)
    assert added is True
    titles = [sp["title"] for sp in bp["sub_pages"]]
    assert any("시작하기" in t for t in titles)
    # 가이드 페이지에 실제 DB명이 반영됨 (템플릿 인지형)
    guide = bp["sub_pages"][-1]
    guide_text = " ".join(b.get("text", "") for b in guide["blocks"])
    assert "프로젝트" in guide_text


def test_inject_onboarding_idempotent():
    bp = _blueprint(sub_pages=[{"title": "시작 가이드", "icon": "📖", "blocks": []}])
    assert inject_onboarding_page(bp) is False
    assert len(bp["sub_pages"]) == 1


def test_inject_top_nav_column_list_for_multiple():
    bp = _blueprint(sub_pages=[{"title": "대시보드", "icon": "📊"}, {"title": "보관함", "icon": "📁"}])
    added = inject_top_nav(bp)
    assert added is True
    col = next((b for b in bp["blocks"] if b.get("type") == "column_list"), None)
    assert col is not None
    refs = [item["sub_page_ref"] for c in col["columns"] for item in c if item.get("type") == "link_to_page"]
    assert "대시보드" in refs and "보관함" in refs
    # 환영 callout 다음에 위치
    assert bp["blocks"][0]["type"] == "callout"
    assert bp["blocks"][1]["type"] == "column_list"


def test_inject_top_nav_single_link_for_one():
    bp = _blueprint(sub_pages=[{"title": "가이드문서", "icon": "📖"}])
    added = inject_top_nav(bp)
    assert added is True
    link = next((b for b in bp["blocks"] if b.get("type") == "link_to_page"), None)
    assert link is not None and link["sub_page_ref"] == "가이드문서"


def test_inject_top_nav_noop_without_subpages():
    bp = _blueprint(sub_pages=[])
    assert inject_top_nav(bp) is False


def test_inject_top_nav_idempotent():
    bp = _blueprint(sub_pages=[{"title": "A"}, {"title": "B"}])
    assert inject_top_nav(bp) is True
    assert inject_top_nav(bp) is False  # 이미 네비 존재


def test_ensure_toc_adds_when_headings_present():
    bp = _blueprint()
    assert ensure_toc(bp) is True
    assert any(b.get("type") == "table_of_contents" for b in bp["blocks"])
    assert ensure_toc(bp) is False  # 멱등


def test_enrich_raises_premium_score():
    bp = _blueprint()
    before = score_blueprint(bp)
    enrich_blueprint(bp)
    after = score_blueprint(bp)

    onboarding_after = next(c for c in after.criteria if c.key == "onboarding")
    nav_after = next(c for c in after.criteria if c.key == "mobile_nav")
    assert onboarding_after.score == 1.0
    assert nav_after.score >= 0.8
    assert after.score > before.score, f"보강 후 점수가 오르지 않음: {before.score} → {after.score}"


def test_enrich_records_applied_in_metadata():
    bp = _blueprint()
    enrich_blueprint(bp)
    applied = bp["metadata"]["sellability_applied"]
    assert "onboarding" in applied and "top_nav" in applied
