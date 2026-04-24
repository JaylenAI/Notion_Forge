from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient


class CreatePageTool(BaseTool):
    name = "create_page"
    description = "새 노션 페이지를 생성합니다"
    parameters = {
        "parent_id": {"type": "string", "description": "부모 페이지 ID"},
        "title": {"type": "string", "description": "페이지 제목"},
        "icon": {"type": "string", "description": "이모지 아이콘", "optional": True},
        "cover_url": {"type": "string", "description": "커버 이미지 URL", "optional": True},
        "children": {"type": "array", "description": "자식 블록 배열", "optional": True},
    }

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
