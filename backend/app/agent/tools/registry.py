"""ToolRegistry: 도구 자동 등록 및 LLM function calling 스펙 생성"""

import logging
from typing import Any

from app.agent.tools.base import BaseTool
from app.notion.client import NotionClient

logger = logging.getLogger("notionforge.tool_registry")


class ToolRegistry:
    def __init__(self, client: NotionClient):
        self._tools: dict[str, BaseTool] = {}
        self._register_all(client)

    def _register_all(self, client: NotionClient) -> None:
        from app.agent.tools.add_blocks import AddBlocksTool
        from app.agent.tools.add_database_items import AddDatabaseItemsTool
        from app.agent.tools.apply_color_theme import ApplyColorThemeTool
        from app.agent.tools.create_columns import CreateColumnsTool
        from app.agent.tools.create_database import CreateDatabaseTool
        from app.agent.tools.create_page import CreatePageTool
        from app.agent.tools.create_view import CreateViewTool
        from app.agent.tools.generate_cover import GenerateCoverTool
        from app.agent.tools.link_databases import LinkDatabasesTool

        for tool in [
            CreatePageTool(client),
            CreateDatabaseTool(client),
            AddBlocksTool(client),
            AddDatabaseItemsTool(client),
            CreateColumnsTool(client),
            LinkDatabasesTool(client),
            CreateViewTool(client),
            ApplyColorThemeTool(),
            GenerateCoverTool(),
        ]:
            self._tools[tool.name] = tool

        logger.info(f"[ToolRegistry] {len(self._tools)}개 도구 등록: {list(self._tools.keys())}")

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def list_names(self) -> list[str]:
        return list(self._tools.keys())

    def get_tool_specs(self) -> list[dict[str, Any]]:
        return [tool.to_tool_spec() for tool in self._tools.values()]

    def get_tool_descriptions(self) -> str:
        return "\n".join(f"- {tool.name}: {tool.description}" for tool in self._tools.values())

    async def execute(self, tool_name: str, **kwargs: Any) -> dict[str, Any]:
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": f"Unknown tool: {tool_name}"}
        try:
            return await tool.execute(**kwargs)
        except Exception as e:
            logger.warning(f"[ToolRegistry] {tool_name} 실행 실패: {e}")
            return {"error": str(e)[:200]}
