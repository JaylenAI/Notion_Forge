from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient


class CreateViewTool(BaseTool):
    name = "create_view"
    description = "데이터베이스에 뷰를 추가합니다 (gallery, board, calendar, timeline, list, chart, form)"
    parameters = {
        "database_id": {"type": "string", "description": "대상 DB ID"},
        "view_type": {
            "type": "string",
            "description": "뷰 타입 (gallery, board, calendar, timeline, list, table, chart, form)",
        },
        "title": {"type": "string", "description": "뷰 제목", "optional": True},
        "group_by": {"type": "string", "description": "그룹화 속성 이름", "optional": True},
        "sorts": {"type": "array", "description": "정렬 [{property, direction}]", "optional": True},
    }

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        group_by = None
        if kwargs.get("group_by"):
            group_by = {"property": kwargs["group_by"], "type": "exact"}

        return await self.client.create_view(
            database_id=kwargs["database_id"],
            view_type=kwargs["view_type"],
            title=kwargs.get("title", ""),
            group_by=group_by,
            sorts=kwargs.get("sorts"),
        )
