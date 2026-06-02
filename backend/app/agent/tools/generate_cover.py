import json
from pathlib import Path
from typing import Any

from app.agent.tools.base import BaseTool

# 커버 URL은 data/cover_urls.json 단일 출처(SSOT)에서 로드. (인라인 8개 중복 제거 — C3)
_COVER_FILE = Path(__file__).resolve().parent.parent / "data" / "cover_urls.json"
_DEFAULT = "https://images.unsplash.com/photo-1557683316-973673baf926?w=1600"


def _load_covers() -> dict[str, list[str]]:
    try:
        data = json.loads(_COVER_FILE.read_text(encoding="utf-8"))
        return {k: (v if isinstance(v, list) else [v]) for k, v in data.items()}
    except Exception:
        return {"default": [_DEFAULT]}


COVER_URLS = _load_covers()


class GenerateCoverTool(BaseTool):
    name = "generate_cover"
    description = "색상 테마에 맞는 커버 이미지 URL을 생성합니다"
    parameters = {
        "color": {"type": "string", "description": "색상 키 (blue, green, red 등)", "optional": True},
    }

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        color = kwargs.get("color", "default")
        urls = COVER_URLS.get(color) or COVER_URLS.get("default") or [_DEFAULT]
        return {"url": urls[0], "color": color}
