from typing import Any
from app.agent.tools.base import BaseTool


class ApplyColorThemeTool(BaseTool):
    name = "apply_color_theme"
    description = "색상 테마 정보를 반환합니다"
    parameters = {
        "theme": {"type": "string", "description": "색상 테마 (blue, green, red 등)", "optional": True},
    }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        theme = kwargs.get("theme", "default")
        return {"theme": theme, "background": f"{theme}_background" if theme != "default" else "default", "text": theme}
