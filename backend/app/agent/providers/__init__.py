"""AI Provider 추상화 — Strategy 패턴

각 프로바이더는 BaseProvider를 상속하여 call() 메서드만 구현.
ProviderRouter가 API 키 기반으로 적절한 프로바이더를 자동 선택.
"""

from app.agent.providers.base import BaseProvider
from app.agent.providers.router import ProviderRouter, create_provider

__all__ = ["BaseProvider", "ProviderRouter", "create_provider"]
