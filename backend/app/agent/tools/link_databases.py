from typing import Any
from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient


class LinkDatabasesTool(BaseTool):
    name = "link_databases"
    description = "데이터베이스 간 Relation을 설정합니다"

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        source_db_id = kwargs["source_db_id"]
        target_db_id = kwargs["target_db_id"]
        relation_name = kwargs.get("relation_name", "관련 항목")
        updates = {"properties": {relation_name: {"relation": {"database_id": target_db_id, "single_property": {}}}}}
        result = await self.client.update_database(source_db_id, updates)
        return {"success": True, "result": result}
