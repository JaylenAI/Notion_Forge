"""widget_builder 유닛 테스트"""

from app.notion.widget_builder import (
    chart_widget,
    filtered_view_widget,
    list_widget,
    number_widget,
    widget_position,
)


class TestChartWidget:
    def test_basic(self):
        w = chart_widget("매출 차트")
        assert w["type"] == "chart"
        assert w["title"] == "매출 차트"
        assert w["chart_type"] == "bar"
        assert "property" not in w

    def test_with_all_options(self):
        pos = widget_position(0, 1, 2, 1)
        w = chart_widget("파이", chart_type="pie", property_name="상태", group_by="카테고리", position=pos)
        assert w["chart_type"] == "pie"
        assert w["property"] == "상태"
        assert w["group_by"] == "카테고리"
        assert w["position"] == pos


class TestNumberWidget:
    def test_basic(self):
        w = number_widget("총 개수", "항목")
        assert w["type"] == "number"
        assert w["aggregation"] == "count"

    def test_with_position(self):
        pos = widget_position(1, 0)
        w = number_widget("합계", "금액", aggregation="sum", position=pos)
        assert w["aggregation"] == "sum"
        assert w["position"]["row"] == 1


class TestListWidget:
    def test_basic(self):
        w = list_widget("최근 항목")
        assert w["type"] == "list"
        assert w["limit"] == 5
        assert "property" not in w

    def test_with_all_options(self):
        pos = widget_position(0, 0, 1, 2)
        w = list_widget(
            "정렬된 목록",
            property_name="이름",
            limit=10,
            sorts=[{"property": "날짜", "direction": "descending"}],
            filters={"property": "상태", "status": {"equals": "진행중"}},
            position=pos,
        )
        assert w["property"] == "이름"
        assert w["limit"] == 10
        assert len(w["sorts"]) == 1
        assert w["filter"]["property"] == "상태"
        assert w["position"]["height"] == 2


class TestFilteredViewWidget:
    def test_basic(self):
        w = filtered_view_widget("필터 뷰")
        assert w["type"] == "filtered_view"
        assert w["view_type"] == "table"
        assert w["limit"] == 10

    def test_with_all_options(self):
        pos = widget_position(2, 0, 2, 1)
        w = filtered_view_widget(
            "보드 뷰",
            view_type="board",
            filters={"property": "상태"},
            sorts=[{"property": "우선순위"}],
            limit=5,
            position=pos,
        )
        assert w["view_type"] == "board"
        assert w["filter"]["property"] == "상태"
        assert w["sorts"][0]["property"] == "우선순위"
        assert w["position"]["width"] == 2


class TestWidgetPosition:
    def test_default(self):
        p = widget_position()
        assert p == {"row": 0, "col": 0, "width": 1, "height": 1}

    def test_custom(self):
        p = widget_position(3, 2, 4, 2)
        assert p["row"] == 3
        assert p["col"] == 2
