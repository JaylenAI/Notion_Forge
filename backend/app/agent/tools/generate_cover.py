from typing import Any
from app.agent.tools.base import BaseTool

COVER_URLS = {
    "blue": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=1200",
    "orange": "https://images.unsplash.com/photo-1504701954957-2010ec3bcec1?w=1200",
    "green": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200",
    "red": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=1200",
    "purple": "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?w=1200",
    "pink": "https://images.unsplash.com/photo-1490750967868-88aa4f44baee?w=1200",
    "yellow": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200",
    "default": "https://images.unsplash.com/photo-1557683316-973673baf926?w=1200",
}


class GenerateCoverTool(BaseTool):
    name = "generate_cover"
    description = "색상 테마에 맞는 커버 이미지 URL을 생성합니다"
    parameters = {
        "color": {"type": "string", "description": "색상 키 (blue, green, red 등)", "optional": True},
    }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        color = kwargs.get("color", "default")
        return {"url": COVER_URLS.get(color, COVER_URLS["default"]), "color": color}
