"""VisualEnrich 단위 테스트 (Phase A3) — 뷰 큐레이션 + 아이콘 보강."""

from app.agent.premium_rubric import score_blueprint
from app.agent.visual_enrich import curate_views, enrich_visuals, ensure_icons


def _db(title, props, views=None):
    return {"title": title, "properties": props, "views": views or [], "sample_items": []}


def test_curate_adds_board_for_status():
    bp = {"databases": [_db("작업", {"이름": "title", "상태": "status"})]}
    added = curate_views(bp)
    views = bp["databases"][0]["views"]
    types = {v["type"] for v in views}
    assert "board" in types and "table" in types
    board = next(v for v in views if v["type"] == "board")
    assert board["group_by"] == {"property": "상태"}
    assert added >= 2


def test_curate_adds_calendar_for_date():
    bp = {"databases": [_db("일정", {"제목": "title", "날짜": "date"})]}
    curate_views(bp)
    types = {v["type"] for v in bp["databases"][0]["views"]}
    assert "calendar" in types
    cal = next(v for v in bp["databases"][0]["views"] if v["type"] == "calendar")
    assert cal["date_property"] == "날짜"


def test_curate_no_extra_for_plain_db():
    bp = {"databases": [_db("목록", {"이름": "title", "메모": "rich_text"})]}
    curate_views(bp)
    types = {v["type"] for v in bp["databases"][0]["views"]}
    assert types == {"table"}


def test_curate_idempotent_respects_existing():
    bp = {
        "databases": [
            _db(
                "작업", {"이름": "title", "상태": "status"}, views=[{"type": "board", "group_by": {"property": "상태"}}]
            )
        ]
    }
    curate_views(bp)
    boards = [v for v in bp["databases"][0]["views"] if v["type"] == "board"]
    assert len(boards) == 1  # 중복 추가 안 함


def test_curate_respects_max_views():
    bp = {"databases": [_db("작업", {"이름": "title", "상태": "status", "날짜": "date"})]}
    curate_views(bp, max_views=2)
    assert len(bp["databases"][0]["views"]) <= 2


def test_ensure_icons_fills_missing():
    bp = {
        "metadata": {"title": "고객 관리"},
        "main_page": {"title": "고객 관리"},
        "databases": [_db("고객", {"이름": "title"}), _db("거래", {"이름": "title"})],
        "sub_pages": [{"title": "메모"}],
    }
    filled = ensure_icons(bp)
    assert filled == 4  # main + 2 db + 1 sub
    assert bp["main_page"]["icon"]
    assert bp["databases"][0]["icon"] == "👥"  # 고객 → 사람
    assert bp["databases"][1]["icon"] == "💰"  # 거래 → 돈
    assert bp["sub_pages"][0]["icon"]


def test_ensure_icons_idempotent():
    bp = {"main_page": {"title": "x", "icon": "🎨"}, "databases": [{"title": "y", "icon": "📊"}], "sub_pages": []}
    assert ensure_icons(bp) == 0
    assert bp["main_page"]["icon"] == "🎨"  # 기존 보존


def test_enrich_visuals_records_and_lifts_visual_score():
    bp = {
        "metadata": {"title": "프로젝트", "color_theme": "blue"},
        "main_page": {"title": "프로젝트", "cover_url": "http://x/c.jpg"},  # 아이콘 없음
        "blocks": [{"type": "callout", "text": "환영"}],
        "databases": [_db("작업", {"이름": "title", "상태": "status"})],
        "sub_pages": [{"title": "가이드"}],
    }
    before = score_blueprint(bp)
    enrich_visuals(bp)
    after = score_blueprint(bp)

    assert bp["metadata"]["visual_enriched"]["icons_filled"] >= 1
    assert bp["metadata"]["visual_enriched"]["views_added"] >= 1
    visual_before = next(c for c in before.criteria if c.key == "visual")
    visual_after = next(c for c in after.criteria if c.key == "visual")
    assert visual_after.score >= visual_before.score
