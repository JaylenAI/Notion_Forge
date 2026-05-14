"""NotionForge를 Notion External Agent로 등록하는 도구"""

from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient


class RegisterAgentTool(BaseTool):
    name = "register_external_agent"
    description = "AI 에이전트를 Notion에 네이티브 등록합니다 (External Agents API)"
    parameters = {
        "name": {"type": "string", "description": "에이전트 이름"},
        "description": {"type": "string", "description": "에이전트 설명"},
        "instructions": {"type": "string", "description": "에이전트 시스템 지침"},
        "tools": {
            "type": "array",
            "description": "에이전트 도구 목록 [{name, description, parameters}]",
            "optional": True,
        },
        "avatar_url": {"type": "string", "description": "아바타 이미지 URL", "optional": True},
    }

    def __init__(self, client: NotionClient):
        self.client = client

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        return await self.client.register_external_agent(
            name=kwargs["name"],
            description=kwargs["description"],
            instructions=kwargs["instructions"],
            tools=kwargs.get("tools"),
            avatar_url=kwargs.get("avatar_url", ""),
        )
