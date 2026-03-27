from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """모든 Agent Tool의 베이스 클래스"""

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Tool 실행. 각 Tool이 구현."""
        ...
