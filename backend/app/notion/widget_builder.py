"""Dashboard 위젯 빌더 (API 2026-03-11)

Dashboard 뷰의 위젯 configuration 생성 헬퍼.
지원 위젯: chart, number, list, table, filtered_view
"""

from typing import Any


def chart_widget(
    title: str,
    chart_type: str = "bar",
    property_name: str = "",
    group_by: str = "",
    position: dict[str, int] | None = None,
) -> dict[str, Any]:
    """chart_type: bar, line, pie, donut"""
    widget: dict[str, Any] = {
        "type": "chart",
        "title": title,
        "chart_type": chart_type,
    }
    if property_name:
        widget["property"] = property_name
    if group_by:
        widget["group_by"] = group_by
    if position:
        widget["position"] = position
    return widget


def number_widget(
    title: str,
    property_name: str,
    aggregation: str = "count",
    position: dict[str, int] | None = None,
) -> dict[str, Any]:
    """aggregation: count, sum, average, min, max, median, range, percent_empty, percent_not_empty"""
    widget: dict[str, Any] = {
        "type": "number",
        "title": title,
        "property": property_name,
        "aggregation": aggregation,
    }
    if position:
        widget["position"] = position
    return widget


def list_widget(
    title: str,
    property_name: str = "",
    limit: int = 5,
    sorts: list[dict] | None = None,
    filters: dict | None = None,
    position: dict[str, int] | None = None,
) -> dict[str, Any]:
    widget: dict[str, Any] = {
        "type": "list",
        "title": title,
        "limit": limit,
    }
    if property_name:
        widget["property"] = property_name
    if sorts:
        widget["sorts"] = sorts
    if filters:
        widget["filter"] = filters
    if position:
        widget["position"] = position
    return widget


def filtered_view_widget(
    title: str,
    view_type: str = "table",
    filters: dict | None = None,
    sorts: list[dict] | None = None,
    limit: int = 10,
    position: dict[str, int] | None = None,
) -> dict[str, Any]:
    widget: dict[str, Any] = {
        "type": "filtered_view",
        "title": title,
        "view_type": view_type,
        "limit": limit,
    }
    if filters:
        widget["filter"] = filters
    if sorts:
        widget["sorts"] = sorts
    if position:
        widget["position"] = position
    return widget


def widget_position(row: int = 0, col: int = 0, width: int = 1, height: int = 1) -> dict[str, int]:
    return {"row": row, "col": col, "width": width, "height": height}
