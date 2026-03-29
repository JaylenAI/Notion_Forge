"""페이지에 블록 추가 — 전체 블록 타입 지원"""

from typing import Any

from app.agent.tools.base import BaseTool
from app.notion import block_builder as bb
from app.notion.client import NotionClient


class AddBlocksTool(BaseTool):
    name = "add_blocks"
    description = "페이지에 블록을 추가합니다"

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        page_id = kwargs["page_id"]
        block_specs = kwargs["blocks"]
        notion_blocks = [spec_to_block(spec) for spec in block_specs if spec.get("type") != "database_ref"]
        results = await self.client.add_blocks(page_id, notion_blocks)
        return {"block_count": len(results), "results": results}


def spec_to_block(spec: dict) -> dict:
    """Blueprint 블록 스펙 → Notion API 블록 JSON

    지원 블록: paragraph, heading_1~4, callout, toggle, to_do, divider,
    bulleted_list, numbered_list, quote, table, code, bookmark, image,
    video, audio, file, pdf, embed, equation, breadcrumb,
    table_of_contents, column_list, tab, synced_block, toggle_heading
    """
    t = spec["type"]

    # ---- 기본 블록 ----
    if t.startswith("heading_"):
        level = int(t.split("_")[1])
        return bb.heading(
            spec.get("text", ""),
            level=level,
            color=spec.get("color", "default"),
            is_toggleable=spec.get("is_toggleable", False),
            children=[spec_to_block(c) for c in spec["children"]] if spec.get("is_toggleable") and spec.get("children") else None,
        )
    elif t == "toggle_heading":
        level = spec.get("level", 1)
        children = [spec_to_block(c) for c in spec.get("children", [])] if spec.get("children") else [bb.paragraph("")]
        return bb.heading(spec.get("text", ""), level=level, color=spec.get("color", "default"), is_toggleable=True, children=children)
    elif t == "paragraph":
        return bb.paragraph(spec.get("text", ""), color=spec.get("color", "default"))
    elif t == "callout":
        children = [spec_to_block(c) for c in spec["children"]] if spec.get("children") else None
        return bb.callout(spec.get("text", ""), icon=spec.get("icon", "📌"), color=spec.get("color", "default"), children=children)
    elif t == "toggle":
        children = [bb.paragraph(spec["children_text"])] if "children_text" in spec else None
        if spec.get("children") and not children:
            children = [spec_to_block(c) for c in spec["children"]]
        return bb.toggle(spec.get("text", ""), children=children, color=spec.get("color", "default"))
    elif t == "to_do":
        return bb.to_do(spec.get("text", ""), checked=spec.get("checked", False))
    elif t == "divider":
        return bb.divider()
    elif t == "bulleted_list":
        children = [spec_to_block(c) for c in spec["children"]] if spec.get("children") else None
        return bb.bulleted_list(spec.get("text", ""), color=spec.get("color", "default"), children=children)
    elif t == "numbered_list":
        children = [spec_to_block(c) for c in spec["children"]] if spec.get("children") else None
        return bb.numbered_list(spec.get("text", ""), color=spec.get("color", "default"), children=children)
    elif t == "quote":
        children = [spec_to_block(c) for c in spec["children"]] if spec.get("children") else None
        return bb.quote(spec.get("text", ""), color=spec.get("color", "default"), children=children)
    elif t == "table":
        return bb.table(spec.get("rows", [["", ""]]), has_column_header=spec.get("has_column_header", True))

    # ---- 미디어 ----
    elif t == "bookmark" or t == "bookmark_link":
        return bb.bookmark(spec.get("url", ""), caption=spec.get("caption", ""))
    elif t == "image":
        return bb.image(spec.get("url", ""), caption=spec.get("caption", ""))
    elif t == "video":
        return bb.video(spec.get("url", ""), caption=spec.get("caption", ""))
    elif t == "audio":
        return bb.audio(spec.get("url", ""), caption=spec.get("caption", ""))
    elif t == "file":
        return bb.file_block(spec.get("url", ""), name=spec.get("name", ""), caption=spec.get("caption", ""))
    elif t == "pdf":
        return bb.pdf(spec.get("url", ""), caption=spec.get("caption", ""))
    elif t == "code":
        return bb.code_block(spec.get("code", spec.get("text", "")), language=spec.get("language", "python"), caption=spec.get("caption", ""))
    elif t == "embed":
        return bb.embed(spec.get("url", ""), caption=spec.get("caption", ""))

    # ---- 고급 ----
    elif t == "table_of_contents":
        return bb.table_of_contents(color=spec.get("color", "default"))
    elif t == "breadcrumb":
        return bb.breadcrumb()
    elif t == "equation":
        return bb.equation_block(spec.get("expression", ""))
    elif t == "synced_block":
        if spec.get("original_block_id"):
            return bb.synced_block_duplicate(spec["original_block_id"])
        children = [spec_to_block(c) for c in spec.get("children", [])] if spec.get("children") else [bb.paragraph("")]
        return bb.synced_block_original(children)
    elif t == "column_list":
        cols = [
            [spec_to_block(b) for b in c.get("blocks", []) if b.get("type") != "database_ref"]
            for c in spec.get("columns", [])
        ]
        return bb.column_list(cols)
    elif t == "tab":
        return bb.tab_block(spec.get("tabs", []))
    elif t == "link_to_page":
        return bb.link_to_page(spec.get("page_id", ""))
    elif t == "link_to_database":
        return bb.link_to_database(spec.get("database_id", ""))

    # ---- 폴백 ----
    else:
        return bb.paragraph(spec.get("text", f"[{t}]"))
