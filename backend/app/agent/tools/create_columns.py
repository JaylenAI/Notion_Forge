from typing import Any

from app.agent.tools.base import BaseTool
from app.agent.tools.add_blocks import spec_to_block
from app.notion import block_builder as bb
from app.notion.client import NotionClient


class CreateColumnsTool(BaseTool):
    name = "create_columns"
    description = "칼럼 레이아웃을 생성합니다"

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        page_id = kwargs["page_id"]
        columns_spec = kwargs["columns"]
        col_blocks = [[spec_to_block(b) for b in c.get("blocks", []) if b.get("type") != "database_ref"] for c in columns_spec]
        column_block = bb.column_list(col_blocks)
        results = await self.client.add_blocks(page_id, [column_block])
        return {"column_count": len(col_blocks), "results": results}
