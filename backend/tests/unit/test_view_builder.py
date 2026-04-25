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


class TestViewBuilderEdgeCases:
    def test_board_cover_string(self):
        result = build_view_configuration({"type": "board", "cover": "page_cover"})
        assert result["cover"] == {"type": "page_cover"}

    def test_board_cover_aspect(self):
        result = build_view_configuration({"type": "board", "cover_aspect": "contain"})
        assert result["cover_aspect"] == "contain"

    def test_board_card_layout(self):
        result = build_view_configuration({"type": "board", "card_layout": "compact"})
        assert result["card_layout"] == "compact"

    def test_gallery_no_cover(self):
        assert build_view_configuration({"type": "gallery"}) is None

    def test_gallery_card_layout(self):
        result = build_view_configuration({"type": "gallery", "cover": "page_cover", "card_layout": "list"})
        assert result["card_layout"] == "list"

    def test_calendar_no_config(self):
        assert build_view_configuration({"type": "calendar"}) is None

    def test_calendar_show_weekends(self):
        result = build_view_configuration({"type": "calendar", "show_weekends": False})
        assert result["show_weekends"] is False

    def test_chart_no_config(self):
        assert build_view_configuration({"type": "chart"}) is None

    def test_chart_color_theme(self):
        result = build_view_configuration({"type": "chart", "color_theme": "blue"})
        assert result["color_theme"] == "blue"

    def test_chart_show_data_labels(self):
        result = build_view_configuration({"type": "chart", "show_data_labels": True})
        assert result["show_data_labels"] is True

    def test_chart_height(self):
        result = build_view_configuration({"type": "chart", "height": 300})
        assert result["height"] == 300

    def test_timeline_no_config(self):
        assert build_view_configuration({"type": "timeline"}) is None

    def test_timeline_date_property_id(self):
        result = build_view_configuration({"type": "timeline", "date_property_id": "p-id"})
        assert result["date_property_id"] == "p-id"

    def test_timeline_end_date(self):
        result = build_view_configuration({"type": "timeline", "end_date_property_id": "end"})
        assert result["end_date_property_id"] == "end"

    def test_timeline_arrows_by(self):
        result = build_view_configuration({"type": "timeline", "arrows_by": "dep"})
        assert result["arrows_by"] == "dep"

    def test_table_frozen_column(self):
        result = build_view_configuration({"type": "table", "frozen_column_index": 2})
        assert result["frozen_column_index"] == 2

    def test_form_submission_permissions(self):
        result = build_view_configuration({"type": "form", "submission_permissions": "anyone"})
        assert result["submission_permissions"] == "anyone"

    def test_unknown_type_returns_none(self):
        assert build_view_configuration({"type": "unknown_view"}) is None

    def test_board_no_config(self):
        assert build_view_configuration({"type": "board"}) is None
