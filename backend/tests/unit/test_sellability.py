"""Sellability 보강 단위 테스트 (Phase A2) — 보강이 루브릭 점수를 올리는지 검증."""

from app.agent.premium_rubric import score_blueprint
from app.agent.sellability import (
    enrich_blueprint,
    ensure_toc,
    inject_onboarding_page,
    inject_top_nav,
)


def _blueprint(sub_pages=None, blocks=None, databases=None):
    return {
        "metadata": {"title": "프로젝트 관리", "color_theme": "blue"},
        "main_page": {"title": "프로젝트 관리", "icon": "📋", "cover_url": "http://x/c.jpg"},
        "blocks": blocks
        if blocks is not None
        else [
            {"type": "callout", "text": "환영"},
            {"type": "heading_1", "text": "프로젝트"},
            {"type": "database_ref", "db_index": 0},
        ],
        "databases": databases
        if databases is not None
        else [
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


def _complex_blueprint():
    """멀티 DB + 기존 하위페이지 1 + heading 3 — 적응형 셸이 모두 적용되는 복잡한 템플릿."""
    return _blueprint(
        sub_pages=[{"title": "참고자료", "icon": "📁"}],
        databases=[
            {
                "title": "프로젝트",
                "properties": {"이름": "title", "상태": "status"},
                "views": [{"type": "board"}],
                "sample_items": [{"이름": "A"}],
                "description": "프로젝트 추적",
            },
            {
                "title": "작업",
                "properties": {"이름": "title", "담당": "people"},
                "views": [{"type": "table"}],
                "sample_items": [{"이름": "X"}],
                "description": "작업 목록",
            },
        ],
        blocks=[
            {"type": "callout", "text": "환영"},
            {"type": "heading_1", "text": "프로젝트"},
            {"type": "heading_2", "text": "작업"},
            {"type": "heading_2", "text": "통계"},
            {"type": "database_ref", "db_index": 0},
        ],
    )


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


def test_inject_top_nav_skips_single_subpage():
    """적응형: 하위 페이지가 1개뿐이면 가로 네비를 만들지 않는다(단일 링크 = 클러터)."""
    bp = _blueprint(sub_pages=[{"title": "가이드문서", "icon": "📖"}])
    assert inject_top_nav(bp) is False
    assert not any(b.get("type") in ("column_list", "link_to_page") for b in bp["blocks"])


def test_inject_top_nav_noop_without_subpages():
    bp = _blueprint(sub_pages=[])
    assert inject_top_nav(bp) is False


def test_inject_top_nav_idempotent():
    bp = _blueprint(sub_pages=[{"title": "A"}, {"title": "B"}])
    assert inject_top_nav(bp) is True
    assert inject_top_nav(bp) is False  # 이미 네비 존재


def test_ensure_toc_adds_when_many_headings():
    """적응형: heading이 3개 이상인 섹션 많은 템플릿에만 목차를 추가한다."""
    bp = _complex_blueprint()  # heading 3개
    assert ensure_toc(bp) is True
    assert any(b.get("type") == "table_of_contents" for b in bp["blocks"])
    assert ensure_toc(bp) is False  # 멱등


def test_ensure_toc_skips_when_few_headings():
    """적응형: heading이 적은(<3) 단순 템플릿엔 목차를 강제하지 않는다."""
    bp = _blueprint()  # heading 1개
    assert ensure_toc(bp) is False
    assert not any(b.get("type") == "table_of_contents" for b in bp["blocks"])


def test_enrich_raises_premium_score():
    bp = _complex_blueprint()  # 멀티 DB → 적응형 셸 모두 적용
    before = score_blueprint(bp)
    enrich_blueprint(bp)
    after = score_blueprint(bp)

    onboarding_after = next(c for c in after.criteria if c.key == "onboarding")
    nav_after = next(c for c in after.criteria if c.key == "mobile_nav")
    assert onboarding_after.score == 1.0
    assert nav_after.score >= 0.8
    assert after.score > before.score, f"보강 후 점수가 오르지 않음: {before.score} → {after.score}"


def test_enrich_records_applied_in_metadata():
    bp = _complex_blueprint()
    enrich_blueprint(bp)
    applied = bp["metadata"]["sellability_applied"]
    assert "onboarding" in applied and "top_nav" in applied


def test_enrich_minimal_for_simple_single_db():
    """적응형 핵심: 단일 DB 단순 템플릿엔 온보딩 페이지를 강제하지 않는다(다양성 보존)."""
    bp = _blueprint()  # 단일 DB
    enrich_blueprint(bp)
    applied = bp["metadata"]["sellability_applied"]
    assert "onboarding" not in applied
    titles = [sp.get("title", "") for sp in bp["sub_pages"]]
    assert not any("시작하기" in t for t in titles)
