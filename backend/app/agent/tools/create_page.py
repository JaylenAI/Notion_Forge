from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient


class CreatePageTool(BaseTool):
    name = "create_page"
    description = "새 노션 페이지를 생성합니다"

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        return await self.client.create_page(
            parent_id=kwargs["parent_id"],
            title=kwargs["title"],
            icon=kwargs.get("icon"),
            cover_url=kwargs.get("cover_url"),
            children=kwargs.get("children"),
        )
