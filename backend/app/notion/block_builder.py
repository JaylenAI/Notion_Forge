"""Notion API 블록 JSON 빌더 — 전체 블록 타입 지원

Phase A: 기본 블록 (heading_4, table, quote)
Phase B: 인라인 서식 (italic, underline, strikethrough, code, link, equation)
Phase C: 미디어 (code block, video, audio, file, pdf)
Phase D: 고급 (breadcrumb, synced_block, 4~5단 칼럼, 토글 제목, equation block, comment)
Phase E: 임베드 (embed 블록)
"""

from typing import Any

# ============================================================
# 색상 유효성 검사
# ============================================================

VALID_COLORS = {
    "default",
    "gray",
    "brown",
    "orange",
    "yellow",
    "green",
    "blue",
    "purple",
    "pink",
    "red",
    "gray_background",
    "brown_background",
    "orange_background",
    "yellow_background",
    "green_background",
    "blue_background",
    "purple_background",
    "pink_background",
    "red_background",
}


def _safe_color(color: str) -> str:
    return color if color in VALID_COLORS else "default"


# Notion number 속성이 허용하는 포맷 (한국어 별칭 매핑 포함)
VALID_NUMBER_FORMATS = {
    "number",
    "number_with_commas",
    "percent",
    "dollar",
    "euro",
    "pound",
    "yen",
    "won",
    "yuan",
    "rupee",
    "real",
    "franc",
}
_NUMBER_FORMAT_ALIASES = {
    "원": "won",
    "krw": "won",
    "달러": "dollar",
    "usd": "dollar",
    "퍼센트": "percent",
    "%": "percent",
    "엔": "yen",
    "콤마": "number_with_commas",
    "천단위": "number_with_commas",
}


def _safe_number_format(fmt: str) -> str:
    f = str(fmt).strip().lower()
    f = _NUMBER_FORMAT_ALIASES.get(f, f)
    return f if f in VALID_NUMBER_FORMATS else "number"


# ============================================================
# Phase B: Rich Text (인라인 서식 전체 지원)
# ============================================================


def rich_text(
    content: str,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    strikethrough: bool = False,
    code: bool = False,
    color: str = "default",
    link: str | None = None,
) -> list[dict]:
    """Rich text 배열 생성 — 모든 인라인 서식 지원"""
    annotations = {
        "bold": bold,
        "italic": italic,
        "underline": underline,
        "strikethrough": strikethrough,
        "code": code,
        "color": _safe_color(color),
    }
    text_obj: dict[str, Any] = {"content": content}
    if link:
        text_obj["link"] = {"url": link}
    return [{"type": "text", "text": text_obj, "annotations": annotations}]


def rich_text_array(segments: list[dict]) -> list[dict]:
    """혼합 서식 리치텍스트 배열 생성 — bold+color, italic+link 등 복합 서식

    segments: [
        {"text": "볼드텍스트", "bold": true, "color": "blue"},
        {"text": " 일반 ", },
        {"text": "링크", "link": "https://...", "italic": true},
    ]
    """
    result = []
    for seg in segments:
        text_content = seg.get("text", seg.get("content", ""))
        annotations = {
            "bold": seg.get("bold", False),
            "italic": seg.get("italic", False),
            "underline": seg.get("underline", False),
            "strikethrough": seg.get("strikethrough", False),
            "code": seg.get("code", False),
            "color": _safe_color(seg.get("color", "default")),
        }
        text_obj: dict[str, Any] = {"content": text_content}
        if seg.get("link"):
            text_obj["link"] = {"url": seg["link"]}
        result.append({"type": "text", "text": text_obj, "annotations": annotations})
    return result


def rich_text_equation(expression: str) -> list[dict]:
    """인라인 수식 (LaTeX)"""
    return [{"type": "equation", "equation": {"expression": expression}}]


def rich_text_mention_page(page_id: str) -> list[dict]:
    """페이지 멘션 (인라인)"""
    return [{"type": "mention", "mention": {"type": "page", "page": {"id": page_id}}}]


def rich_text_mention_date(start: str, end: str | None = None) -> list[dict]:
    """날짜 멘션 (인라인)"""
    date_obj: dict[str, Any] = {"start": start}
    if end:
        date_obj["end"] = end
    return [{"type": "mention", "mention": {"type": "date", "date": date_obj}}]


def rich_text_mention_user(user_id: str) -> list[dict]:
    """유저 멘션 (인라인)"""
    return [{"type": "mention", "mention": {"type": "user", "user": {"id": user_id}}}]


def rich_text_mention_database(database_id: str) -> list[dict]:
    """DB 멘션 (인라인)"""
    return [{"type": "mention", "mention": {"type": "database", "database": {"id": database_id}}}]


def rich_text_template_mention(template_type: str = "today") -> list[dict]:
    """템플릿 멘션 (@today, @now, @me)"""
    if template_type == "me":
        return [
            {
                "type": "mention",
                "mention": {
                    "type": "template_mention",
                    "template_mention": {"type": "template_mention_user", "template_mention_user": "me"},
                },
            }
        ]
    return [
        {
            "type": "mention",
            "mention": {
                "type": "template_mention",
                "template_mention": {"type": "template_mention_date", "template_mention_date": template_type},
            },
        }
    ]


# ============================================================
# Phase A: 기본 블록 (전체)
# ============================================================


def heading(
    text: str, level: int = 1, color: str = "default", is_toggleable: bool = False, children: list[dict] | None = None
) -> dict[str, Any]:
    """heading_1/2/3/4 블록 — 토글 제목 지원"""
    key = f"heading_{level}"
    block: dict[str, Any] = {
        "object": "block",
        "type": key,
        key: {"rich_text": rich_text(text), "color": _safe_color(color), "is_toggleable": is_toggleable},
    }
    if is_toggleable and children:
        block[key]["children"] = children
    return block


def paragraph(text: str, color: str = "default") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": rich_text(text), "color": _safe_color(color)},
    }


def callout(text: str, icon: str = "📌", color: str = "default", children: list[dict] | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": rich_text(text),
            "icon": {"type": "emoji", "emoji": icon},
            "color": _safe_color(color),
        },
    }
    if children:
        block["callout"]["children"] = children
    return block


def toggle(text: str, children: list[dict] | None = None, color: str = "default") -> dict[str, Any]:
    block: dict[str, Any] = {
        "object": "block",
        "type": "toggle",
        "toggle": {"rich_text": rich_text(text), "color": _safe_color(color)},
    }
    if children:
        block["toggle"]["children"] = children
    return block


def to_do(text: str, checked: bool = False, color: str = "default") -> dict[str, Any]:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {"rich_text": rich_text(text), "checked": checked, "color": _safe_color(color)},
    }


def divider() -> dict[str, Any]:
    return {"object": "block", "type": "divider", "divider": {}}


def bulleted_list(text: str, color: str = "default", children: list[dict] | None = None) -> dict[str, Any]:
    block: dict[str, Any] = {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": rich_text(text), "color": _safe_color(color)},
    }
    if children:
        block["bulleted_list_item"]["children"] = children
    return block


def numbered_list(
    text: str,
    color: str = "default",
    children: list[dict] | None = None,
    list_format: str = "",
    list_start_index: int | None = None,
) -> dict[str, Any]:
    item: dict[str, Any] = {"rich_text": rich_text(text), "color": _safe_color(color)}
    if list_format and list_format in ("numbers", "letters", "roman"):
        item["list_format"] = list_format
    if list_start_index is not None:
        item["list_start_index"] = list_start_index
    block: dict[str, Any] = {
        "object": "block",
        "type": "numbered_list_item",
        "numbered_list_item": item,
    }
    if children:
        block["numbered_list_item"]["children"] = children
    return block


def quote(text: str, color: str = "default", children: list[dict] | None = None) -> dict[str, Any]:
    """인용 블록"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "quote",
        "quote": {"rich_text": rich_text(text), "color": _safe_color(color)},
    }
    if children:
        block["quote"]["children"] = children
    return block


def table(rows: list[list[str]], has_column_header: bool = True, has_row_header: bool = False) -> dict[str, Any]:
    """정적 테이블 블록"""
    if not rows:
        rows = [["", ""]]
    width = len(rows[0])
    table_rows = []
    for row in rows:
        cells = [rich_text(cell) for cell in row]
        # 폭 맞추기
        while len(cells) < width:
            cells.append(rich_text(""))
        table_rows.append(
            {
                "object": "block",
                "type": "table_row",
                "table_row": {"cells": cells},
            }
        )
    return {
        "object": "block",
        "type": "table",
        "table": {
            "table_width": width,
            "has_column_header": has_column_header,
            "has_row_header": has_row_header,
            "children": table_rows,
        },
    }


# ============================================================
# Phase C: 미디어 블록
# ============================================================


def bookmark(url: str, caption: str = "") -> dict[str, Any]:
    block: dict[str, Any] = {"object": "block", "type": "bookmark", "bookmark": {"url": url}}
    if caption:
        block["bookmark"]["caption"] = rich_text(caption)
    return block


def image(url: str, caption: str = "") -> dict[str, Any]:
    block: dict[str, Any] = {
        "object": "block",
        "type": "image",
        "image": {"type": "external", "external": {"url": url}},
    }
    if caption:
        block["image"]["caption"] = rich_text(caption)
    return block


def video(url: str, caption: str = "") -> dict[str, Any]:
    """비디오 블록 (external URL)"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "video",
        "video": {"type": "external", "external": {"url": url}},
    }
    if caption:
        block["video"]["caption"] = rich_text(caption)
    return block


def audio(url: str, caption: str = "") -> dict[str, Any]:
    """오디오 블록 (external URL)"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "audio",
        "audio": {"type": "external", "external": {"url": url}},
    }
    if caption:
        block["audio"]["caption"] = rich_text(caption)
    return block


def file_block(url: str, name: str = "", caption: str = "") -> dict[str, Any]:
    """파일 블록 (external URL)"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "file",
        "file": {"type": "external", "external": {"url": url}},
    }
    if name:
        block["file"]["name"] = name
    if caption:
        block["file"]["caption"] = rich_text(caption)
    return block


def pdf(url: str, caption: str = "") -> dict[str, Any]:
    """PDF 블록 (external URL)"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "pdf",
        "pdf": {"type": "external", "external": {"url": url}},
    }
    if caption:
        block["pdf"]["caption"] = rich_text(caption)
    return block


def code_block(code: str, language: str = "python", caption: str = "") -> dict[str, Any]:
    """코드 블록 (60+ 언어 지원)"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "code",
        "code": {"rich_text": rich_text(code), "language": language},
    }
    if caption:
        block["code"]["caption"] = rich_text(caption)
    return block


# ============================================================
# Phase D: 고급 블록
# ============================================================


def table_of_contents(color: str = "default") -> dict[str, Any]:
    return {"object": "block", "type": "table_of_contents", "table_of_contents": {"color": _safe_color(color)}}


def breadcrumb() -> dict[str, Any]:
    """경로 블록"""
    return {"object": "block", "type": "breadcrumb", "breadcrumb": {}}


def equation_block(expression: str) -> dict[str, Any]:
    """수식 블록 (display mode, KaTeX)"""
    return {"object": "block", "type": "equation", "equation": {"expression": expression}}


def synced_block_original(children: list[dict]) -> dict[str, Any]:
    """동기화 블록 (원본 생성)"""
    return {
        "object": "block",
        "type": "synced_block",
        "synced_block": {"synced_from": None, "children": children},
    }


def synced_block_duplicate(original_block_id: str) -> dict[str, Any]:
    """동기화 블록 (복제)"""
    return {
        "object": "block",
        "type": "synced_block",
        "synced_block": {"synced_from": {"block_id": original_block_id}},
    }


def column_list(columns: list[list[dict]], width_ratios: list[float] | None = None) -> dict[str, Any]:
    """N단 칼럼 (2~5단). width_ratios로 비율 지정 가능 (예: [0.3, 0.7])"""
    children = []
    for i, col_blocks in enumerate(columns):
        col: dict[str, Any] = {"children": col_blocks}
        if width_ratios and i < len(width_ratios):
            col["width_ratio"] = width_ratios[i]
        children.append({"object": "block", "type": "column", "column": col})
    return {
        "object": "block",
        "type": "column_list",
        "column_list": {"children": children},
    }


def link_to_page(page_id: str) -> dict[str, Any]:
    return {
        "object": "block",
        "type": "link_to_page",
        "link_to_page": {"type": "page_id", "page_id": page_id},
    }


def link_to_database(database_id: str) -> dict[str, Any]:
    """DB 링크 블록"""
    return {
        "object": "block",
        "type": "link_to_page",
        "link_to_page": {"type": "database_id", "database_id": database_id},
    }


def tab_block(tabs: list[dict[str, Any]]) -> dict[str, Any]:
    """Tab 블록 (2026-03-25)"""
    tab_children = []
    for tab in tabs:
        tab_content = tab.get("children", [paragraph(tab.get("label", "탭"))])
        label_block: dict[str, Any] = {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": rich_text(tab.get("label", "탭")),
                "children": tab_content if isinstance(tab_content, list) else [tab_content],
            },
        }
        if tab.get("icon"):
            label_block["paragraph"]["icon"] = {"type": "emoji", "emoji": tab["icon"]}
        tab_children.append(label_block)
    return {"object": "block", "type": "tab", "tab": {"children": tab_children}}


# ============================================================
# Phase E: 임베드
# ============================================================


def embed(url: str, caption: str = "") -> dict[str, Any]:
    """임베드 블록 (Google Drive, Figma, GitHub, Tweet, Loom, Miro 등)"""
    block: dict[str, Any] = {
        "object": "block",
        "type": "embed",
        "embed": {"url": url},
    }
    if caption:
        block["embed"]["caption"] = rich_text(caption)
    return block


# ============================================================
# Phase F: 버튼 블록
# ============================================================


def button(label: str, actions: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """버튼 블록 — Notion 자동화 트리거

    actions 예시:
    - {"type": "open_url", "url": "https://..."}
    - {"type": "set_property", "property": "상태", "value": "완료"}
    - {"type": "create_page", "parent_id": "...", "title": "New"}
    """
    block: dict[str, Any] = {
        "object": "block",
        "type": "button",
        "button": {
            "rich_text": rich_text(label),
        },
    }
    if actions:
        block["button"]["actions"] = actions
    return block


# ============================================================
# 멘션 헬퍼 (하위 호환)
# ============================================================


def mention_page(page_id: str, text: str = "") -> dict[str, Any]:
    return {"type": "mention", "mention": {"type": "page", "page": {"id": page_id}}, "plain_text": text}


def mention_date(start: str, end: str | None = None) -> dict[str, Any]:
    date_obj: dict[str, Any] = {"start": start}
    if end:
        date_obj["end"] = end
    return {"type": "mention", "mention": {"type": "date", "date": date_obj}}


# ============================================================
# 아이콘 헬퍼
# ============================================================


def icon_emoji(emoji: str) -> dict:
    return {"type": "emoji", "emoji": emoji}


def icon_external(url: str) -> dict:
    return {"type": "external", "external": {"url": url}}


def icon_native(name: str, color: str = "default") -> dict:
    """Native Notion icon (2026-03)"""
    return {"type": "icon", "icon": {"name": name, "color": color}}


def icon_custom_emoji(custom_emoji_id: str) -> dict:
    return {"type": "custom_emoji", "custom_emoji": {"id": custom_emoji_id}}


# ============================================================
# DB 속성 빌더
# ============================================================


def build_database_properties(props: dict[str, Any]) -> dict[str, Any]:
    """DB 속성 스키마 생성"""
    # AI가 잘못 생성할 수 있는 타입명 → Notion API 올바른 타입명
    type_aliases = {
        "text": "rich_text",
        "string": "rich_text",
        "memo": "rich_text",
        "integer": "number",
        "float": "number",
        "bool": "checkbox",
        "boolean": "checkbox",
        "tag": "select",
        "tags": "multi_select",
        "link": "url",
        "person": "rich_text",  # people은 user ID 필요 → 텍스트로 대체
        "file": "files",
        "phone": "phone_number",
        "created": "created_time",
        "updated": "last_edited_time",
    }

    result = {}

    # title 속성이 반드시 하나 있어야 함 (Notion 필수)
    has_title = any(
        (isinstance(s, str) and s == "title") or (isinstance(s, dict) and s.get("type") == "title")
        for s in props.values()
    )
    if not has_title:
        # 첫 번째 속성을 title로 강제 변환, 또는 "이름" 추가
        first_key = next(iter(props), None)
        if first_key:
            result[first_key] = {"title": {}}
            props = {k: v for k, v in props.items() if k != first_key}
        else:
            result["이름"] = {"title": {}}

    for name, spec in props.items():
        if isinstance(spec, str):
            # 타입 별칭 자동 변환
            spec = type_aliases.get(spec, spec)
            if spec in ("created_time", "created_by", "last_edited_time", "last_edited_by", "unique_id"):
                result[name] = {spec: {}}
                continue
            result[name] = {spec: {}}
        elif isinstance(spec, dict):
            prop_type = type_aliases.get(spec["type"], spec["type"])
            config: dict[str, Any] = {}
            # select/multi_select 옵션 색상 검증
            valid_option_colors = {
                "default",
                "gray",
                "brown",
                "orange",
                "yellow",
                "green",
                "blue",
                "purple",
                "pink",
                "red",
            }
            if prop_type in ("select", "multi_select") and "options" in spec:
                config["options"] = [
                    {
                        "name": str(opt["name"] if isinstance(opt, dict) else opt),
                        "color": (
                            opt.get("color", "default")
                            if isinstance(opt, dict) and opt.get("color") in valid_option_colors
                            else "default"
                        ),
                    }
                    for opt in spec["options"]
                ]
            elif prop_type == "status" and "options" in spec:
                config["options"] = spec["options"]
            elif prop_type == "relation" and "database_id" in spec:
                config["database_id"] = spec["database_id"]
                if spec.get("single_property"):
                    config["single_property"] = {}
            elif prop_type == "formula" and "expression" in spec:
                config["expression"] = spec["expression"]
            elif prop_type == "rollup" and "relation_property_name" in spec:
                config["relation_property_name"] = spec["relation_property_name"]
                config["rollup_property_name"] = spec["rollup_property_name"]
                config["function"] = spec.get("function", "count")
            elif prop_type == "number" and "format" in spec:
                # 통화/퍼센트 등 숫자 포맷 (won/dollar/euro/yen/percent/number ...)
                config["format"] = _safe_number_format(spec["format"])
            result[name] = {prop_type: config}
    return result
