"""ListingKit 단위 테스트 (Phase A2)."""

from app.agent.listing_kit import build_listing_kit


def _multidb_blueprint():
    return {
        "metadata": {"title": "CRM 대시보드", "color_theme": "blue"},
        "main_page": {"title": "CRM 대시보드"},
        "blocks": [{"type": "callout", "text": "환영"}],
        "databases": [
            {
                "title": "고객",
                "properties": {
                    "고객명": "title",
                    "총딜금액": {"type": "rollup", "relation_property": "딜"},
                    "딜": {"type": "relation", "target_db_index": 1},
                },
                "views": [{"type": "table"}, {"type": "board"}],
                "sample_items": [{"고객명": "A"}, {"고객명": "B"}],
            },
            {
                "title": "딜",
                "properties": {"딜명": "title", "남은일수": {"type": "formula", "expression": "1"}},
                "views": [{"type": "calendar"}],
                "sample_items": [{"딜명": "딜1"}, {"딜명": "딜2"}],
            },
        ],
        "sub_pages": [{"title": "🚀 시작하기"}],
    }


def test_listing_kit_has_required_keys():
    kit = build_listing_kit(_multidb_blueprint())
    assert set(kit) >= {"title", "tagline", "description", "features", "preview_script", "suggested_price_band"}
    assert kit["title"] == "CRM 대시보드"


def test_listing_kit_features_reflect_structure():
    kit = build_listing_kit(_multidb_blueprint())
    blob = " ".join(kit["features"])
    assert "rollup" in blob  # 집계 기능 노출
    assert "formula" in blob  # 수식 기능 노출
    assert any("연결 데이터베이스" in f for f in kit["features"])
    assert kit["preview_script"]  # 비어있지 않음


def test_listing_kit_price_band_is_valid():
    kit = build_listing_kit(_multidb_blueprint())
    assert kit["suggested_price_band"] in ("$0", "$5-15", "$20-49", "$50-99", "$100+")


def test_listing_kit_single_db():
    bp = {
        "metadata": {"title": "독서 기록"},
        "main_page": {"title": "독서 기록"},
        "blocks": [],
        "databases": [
            {"title": "책", "properties": {"제목": "title"}, "views": [{"type": "table"}], "sample_items": []}
        ],
        "sub_pages": [],
    }
    kit = build_listing_kit(bp)
    assert "독서 기록" in kit["title"]
    assert kit["features"]
