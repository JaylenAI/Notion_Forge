"""Notion Workers API 클라이언트 + External Agents API (2026-03-11)

Notion Workers: 서버리스 TypeScript 런타임
- Syncs: 외부 데이터 → Notion DB 동기화
- Tools: 사용자가 실행할 수 있는 커스텀 액션
- Webhooks: 이벤트 기반 자동화

External Agents API (Alpha):
- AI 에이전트를 Notion에 네이티브 등록
- 에이전트가 Notion 내에서 직접 호출 가능
"""

import logging
from typing import Any

logger = logging.getLogger("notionforge.notion_client")


class WorkerOpsMixin:
    """Notion Workers + External Agents API 작업"""

    # ─── Workers 관리 ───

    async def list_workers(self) -> list[dict]:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get("/workers")
            if resp.status_code >= 400:
                logger.warning(f"[list_workers 에러 {resp.status_code}] {resp.text[:200]}")
                return []
            return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"[list_workers 에러] {str(e)[:100]}")
            return []

    async def get_worker(self, worker_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": worker_id, "status": "active"}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/workers/{worker_id}")
            if resp.status_code >= 400:
                return {"id": worker_id}
            return resp.json()
        except Exception as e:
            logger.warning(f"[get_worker 에러] {str(e)[:100]}")
            return {"id": worker_id}

    async def deploy_worker(
        self,
        title: str,
        worker_type: str,
        code: str,
        database_id: str = "",
        description: str = "",
    ) -> dict[str, Any]:
        """Worker 배포 (type: sync, tool, webhook)"""
        if self.mock_mode:
            return {
                "id": self._mock_id(),
                "title": title,
                "type": worker_type,
                "status": "deploying",
            }

        body: dict[str, Any] = {
            "title": title,
            "type": worker_type,
            "code": code,
        }
        if database_id:
            body["database_id"] = database_id
        if description:
            body["description"] = description

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/workers", json=body)
            if resp.status_code >= 400:
                error_text = resp.text[:300]
                logger.warning(f"[deploy_worker 에러 {resp.status_code}] {error_text}")
                return {"id": self._mock_id(), "title": title, "status": "error", "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[deploy_worker 에러] {str(e)[:100]}")
            return {"id": self._mock_id(), "title": title, "status": "error", "fallback": True}

    async def update_worker(self, worker_id: str, **kwargs) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": worker_id, **kwargs}
        body = {k: v for k, v in kwargs.items() if v is not None}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.patch(f"/workers/{worker_id}", json=body)
            if resp.status_code >= 400:
                logger.warning(f"[update_worker 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": worker_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_worker 에러] {str(e)[:100]}")
            return {"id": worker_id, "fallback": True}

    async def delete_worker(self, worker_id: str) -> bool:
        if self.mock_mode:
            return True
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.delete(f"/workers/{worker_id}")
            if resp.status_code >= 400:
                logger.warning(f"[delete_worker 에러 {resp.status_code}] {resp.text[:200]}")
                return False
            return True
        except Exception as e:
            logger.warning(f"[delete_worker 에러] {str(e)[:100]}")
            return False

    async def get_worker_logs(self, worker_id: str, limit: int = 50) -> list[dict]:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(
                f"/workers/{worker_id}/logs",
                params={"limit": min(limit, 100)},
            )
            if resp.status_code >= 400:
                return []
            return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"[worker_logs 에러] {str(e)[:100]}")
            return []

    # ─── External Agents API (Alpha) ───

    async def register_external_agent(
        self,
        name: str,
        description: str,
        instructions: str,
        tools: list[dict[str, Any]] | None = None,
        avatar_url: str = "",
    ) -> dict[str, Any]:
        """외부 AI 에이전트를 Notion에 네이티브 등록"""
        if self.mock_mode:
            return {
                "id": self._mock_id(),
                "name": name,
                "status": "registered",
            }

        body: dict[str, Any] = {
            "name": name,
            "description": description,
            "instructions": instructions,
        }
        if tools:
            body["tools"] = tools
        if avatar_url:
            body["avatar"] = {"type": "external", "external": {"url": avatar_url}}

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/external_agents", json=body)
            if resp.status_code >= 400:
                logger.warning(f"[register_agent 에러 {resp.status_code}] {resp.text[:300]}")
                return {"id": self._mock_id(), "name": name, "status": "error", "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[register_agent 에러] {str(e)[:100]}")
            return {"id": self._mock_id(), "name": name, "status": "error", "fallback": True}

    async def list_external_agents(self) -> list[dict]:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get("/external_agents")
            if resp.status_code >= 400:
                return []
            return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"[list_agents 에러] {str(e)[:100]}")
            return []

    async def update_external_agent(self, agent_id: str, **kwargs) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": agent_id, **kwargs}
        body = {k: v for k, v in kwargs.items() if v is not None}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.patch(f"/external_agents/{agent_id}", json=body)
            if resp.status_code >= 400:
                logger.warning(f"[update_agent 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": agent_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_agent 에러] {str(e)[:100]}")
            return {"id": agent_id, "fallback": True}

    async def delete_external_agent(self, agent_id: str) -> bool:
        if self.mock_mode:
            return True
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.delete(f"/external_agents/{agent_id}")
            if resp.status_code >= 400:
                return False
            return True
        except Exception as e:
            logger.warning(f"[delete_agent 에러] {str(e)[:100]}")
            return False
