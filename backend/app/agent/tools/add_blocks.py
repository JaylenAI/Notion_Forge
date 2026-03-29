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
    t = spec["type"]
    if t.startswith("heading_"):
        return bb.heading(spec.get("text", ""), level=int(t[-1]), color=spec.get("color", "default"))
    elif t == "paragraph":
        return bb.paragraph(spec.get("text", ""), color=spec.get("color", "default"))
    elif t == "callout":
        return bb.callout(spec.get("text", ""), icon=spec.get("icon", "📌"), color=spec.get("color", "default"))
    elif t == "toggle":
        children = [bb.paragraph(spec["children_text"])] if "children_text" in spec else None
        return bb.toggle(spec.get("text", ""), children=children, color=spec.get("color", "default"))
    elif t == "to_do":
        return bb.to_do(spec.get("text", ""), checked=spec.get("checked", False))
    elif t == "divider":
        return bb.divider()
    elif t == "bulleted_list":
        return bb.bulleted_list(spec.get("text", ""), color=spec.get("color", "default"))
    elif t == "numbered_list":
        return bb.numbered_list(spec.get("text", ""), color=spec.get("color", "default"))
    elif t == "column_list":
        cols = [[spec_to_block(b) for b in c.get("blocks", []) if b.get("type") != "database_ref"] for c in spec.get("columns", [])]
        return bb.column_list(cols)
    elif t == "tab":
        return bb.tab_block(spec.get("tabs", []))
    elif t == "bookmark_link":
        return bb.bookmark(spec.get("url", ""))
    elif t == "image":
        return bb.image(spec.get("url", ""))
    elif t == "table_of_contents":
        return bb.table_of_contents()
    else:
        return bb.paragraph(spec.get("text", f"[{t}]"))
