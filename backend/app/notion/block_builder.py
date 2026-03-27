"""Notion API 블록 JSON을 쉽게 생성하는 유틸리티"""

from typing import Any


def rich_text(content: str, bold: bool = False, color: str = "default") -> list[dict]:
    """Rich text 배열 생성"""
    annotations = {"bold": bold, "color": color}
    return [{"type": "text", "text": {"content": content}, "annotations": annotations}]


def heading(text: str, level: int = 1, color: str = "default") -> dict[str, Any]:
    """heading_1/2/3 블록"""
    key = f"heading_{level}"
    return {
        "object": "block",
        "type": key,
        key: {"rich_text": rich_text(text), "color": color},
    }


def paragraph(text: str, color: str = "default") -> dict[str, Any]:
    """paragraph 블록"""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text(text), "color": color},
    }


def callout(text: str, icon: str = "📌", color: str = "default") -> dict[str, Any]:
    """callout 블록"""
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": rich_text(text),
            "icon": {"type": "emoji", "emoji": icon},
            "color": color,
        },
    }


def toggle(text: str, children: list[dict] | None = None, color: str = "default") -> dict[str, Any]:
    """toggle 블록"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "toggle",
        "toggle": {"rich_text": rich_text(text), "color": color},
    }
    if children:
        block["toggle"]["children"] = children
    return block


def to_do(text: str, checked: bool = False) -> dict[str, Any]:
    """to_do 블록"""
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": rich_text(text), "checked": checked},
    }


def divider() -> dict[str, Any]:
    """divider 블록"""
    return {"object": "block", "type": "divider", "divider": {}}


def bulleted_list(text: str, color: str = "default") -> dict[str, Any]:
    """bulleted_list_item 블록"""
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text), "color": color},
    }


def numbered_list(text: str, color: str = "default") -> dict[str, Any]:
    """numbered_list_item 블록"""
    return {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": {"rich_text": rich_text(text), "color": color},
    }


def bookmark(url: str) -> dict[str, Any]:
    """bookmark 블록"""
    return {"object": "block", "type": "bookmark", "bookmark": {"url": url}}


def image(url: str) -> dict[str, Any]:
    """image 블록 (external URL)"""
    return {
        "object": "block",
        "type": "image",
        "image": {"type": "external", "external": {"url": url}},
    }


def table_of_contents() -> dict[str, Any]:
    """table_of_contents 블록"""
    return {"object": "block", "type": "table_of_contents", "table_of_contents": {"color": "default"}}


def column_list(columns: list[list[dict]]) -> dict[str, Any]:
    """column_list + column 블록 생성"""
    return {
        "object": "block",
        "type": "column_list",
        "column_list": {
            "children": [
                {
                    "object": "block",
                    "type": "column",
                    "column": {"children": col_blocks},
                }
                for col_blocks in columns
            ]
        },
    }


def link_to_page(page_id: str) -> dict[str, Any]:
    """link_to_page 블록"""
    return {
        "object": "block",
        "type": "link_to_page",
        "link_to_page": {"type": "page_id", "page_id": page_id},
    }


def build_database_properties(props: dict[str, Any]) -> dict[str, Any]:
    """DB 속성 스키마 생성

    사용법:
        build_database_properties({
            "이름": "title",
            "카테고리": {"type": "select", "options": [{"name": "A", "color": "blue"}]},
            "완료": "checkbox",
            "날짜": "date",
            "링크": "url",
        })
    """
    result = {}
    for name, spec in props.items():
        if isinstance(spec, str):
            result[name] = {spec: {}}
        elif isinstance(spec, dict):
            prop_type = spec["type"]
            config: dict[str, Any] = {}
            if prop_type == "select" and "options" in spec:
                config["options"] = [
                    {"name": opt["name"], "color": opt.get("color", "default")}
                    if isinstance(opt, dict)
                    else {"name": opt, "color": "default"}
                    for opt in spec["options"]
                ]
            elif prop_type == "multi_select" and "options" in spec:
                config["options"] = [
                    {"name": opt["name"], "color": opt.get("color", "default")}
                    if isinstance(opt, dict)
                    else {"name": opt, "color": "default"}
                    for opt in spec["options"]
                ]
            elif prop_type == "status" and "options" in spec:
                config["options"] = spec["options"]
            result[name] = {prop_type: config}
    return result
