"""View Builder 테스트"""

from app.agent.view_builder import build_view_configuration


class TestBuildViewConfiguration:
    def test_board_with_cover(self):
        spec = {"type": "board", "cover": {"type": "page_cover"}, "cover_size": "medium"}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["type"] == "board"
        assert result["cover"]["type"] == "page_cover"

    def test_gallery_with_cover(self):
        spec = {"type": "gallery", "cover": "page_cover", "cover_size": "large"}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["type"] == "gallery"

    def test_calendar_with_date(self):
        spec = {"type": "calendar", "date_property": "due_date_id"}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["date_property_id"] == "due_date_id"

    def test_timeline_with_zoom(self):
        spec = {"type": "timeline", "zoom_level": "month"}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["preference"]["zoom_level"] == "month"

    def test_table_with_wrap(self):
        spec = {"type": "table", "wrap_cells": True}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["wrap_cells"] is True

    def test_chart_with_axes(self):
        spec = {"type": "chart", "chart_type": "bar", "x_axis": "category", "y_axis": "amount"}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["chart_type"] == "bar"

    def test_no_config_returns_none(self):
        spec = {"type": "table"}
        result = build_view_configuration(spec)
        assert result is None

    def test_form_with_permissions(self):
        spec = {"type": "form", "anonymous_submissions": True}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["anonymous_submissions"] is True

    def test_map_with_height(self):
        spec = {"type": "map", "map_by": "location", "height": 400}
        result = build_view_configuration(spec)
        assert result is not None
        assert result["map_by"] == "location"
