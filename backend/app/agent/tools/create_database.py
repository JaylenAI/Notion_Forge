from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.block_builder import build_database_properties
from app.notion.client import NotionClient


class CreateDatabaseTool(BaseTool):
    name = "create_database"
    description = "데이터베이스를 생성하고 속성을 설정합니다"

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        raw_props = kwargs["properties"]
        properties = build_database_properties(raw_props)
        return await self.client.create_database(
            parent_id=kwargs["parent_id"],
            title=kwargs["title"],
            properties=properties,
            is_inline=kwargs.get("is_inline", True),
        )
