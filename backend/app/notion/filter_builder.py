"""Notion 고급 필터 빌더 (API 2026-03-11)

지원:
- 상대 날짜 필터 (today, tomorrow, yesterday, one_week_ago 등)
- Multi-value select/status/multi_select 필터
- "me" 상대 Person 필터
- Compound 필터 (and/or)
"""

from typing import Any

RELATIVE_DATE_VALUES = frozenset(
    {
        "today",
        "tomorrow",
        "yesterday",
        "one_week_ago",
        "one_week_from_now",
        "one_month_ago",
        "one_month_from_now",
    }
)


def date_filter(
    property_name: str,
    operator: str,
    value: str | dict | None = None,
) -> dict[str, Any]:
    f: dict[str, Any] = {"property": property_name}
    if value is None:
        f["date"] = {operator: {}}
    elif isinstance(value, str) and value in RELATIVE_DATE_VALUES:
        f["date"] = {operator: {"relative_date": value}}
    elif isinstance(value, str):
        f["date"] = {operator: value}
    else:
        f["date"] = {operator: value}
    return f


def select_filter(
    property_name: str,
    values: list[str],
    match_type: str = "equals",
) -> dict[str, Any]:
    if len(values) == 1:
        return {"property": property_name, "select": {match_type: values[0]}}
    return {"property": property_name, "select": {match_type: values}}


def multi_select_filter(
    property_name: str,
    values: list[str],
    match_type: str = "contains",
) -> dict[str, Any]:
    if len(values) == 1:
        return {"property": property_name, "multi_select": {match_type: values[0]}}
    return {"property": property_name, "multi_select": {match_type: values}}


def status_filter(
    property_name: str,
    values: list[str],
    match_type: str = "equals",
) -> dict[str, Any]:
    if len(values) == 1:
        return {"property": property_name, "status": {match_type: values[0]}}
    return {"property": property_name, "status": {match_type: values}}


def people_filter(
    property_name: str,
    match_type: str = "contains",
    user_id: str = "me",
) -> dict[str, Any]:
    return {"property": property_name, "people": {match_type: user_id}}


def compound_filter(
    operator: str,
    conditions: list[dict[str, Any]],
) -> dict[str, Any]:
    if operator not in ("and", "or"):
        raise ValueError(f"Invalid operator: {operator}")
    return {operator: conditions}
