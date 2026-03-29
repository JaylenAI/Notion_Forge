"""Notion API Client: 실제 API + Mock 모드 지원

지원 기능:
- 페이지/DB/블록 CRUD
- Views API (갤러리, 캘린더, 칸반 등) — 2026-03-19
- Tab 블록 — 2026-03-25
- Status 속성 쓰기 — 2026-03-19
"""

import uuid
from typing import Any

import httpx

from app.config import settings
from app.notion.rate_limiter import RateLimiter

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2025-09-03"


class NotionClient:
    def __init__(self, token: str = "", parent_page_id: str = ""):
        self.token = token or settings.notion_api_key
        self.parent_page_id = parent_page_id or settings.notion_parent_page_id
        self.mock_mode = not self.token or not self.parent_page_id
        self.rate_limiter = RateLimiter(max_per_second=3)
        self._real_client = None
        self._http_client: httpx.AsyncClient | None = None

        if not self.mock_mode:
            from notion_client import AsyncClient

            self._real_client = AsyncClient(auth=self.token)
            self._http_client = httpx.AsyncClient(
                base_url=NOTION_API_BASE,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": NOTION_VERSION,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )

    # ========================================
    # 페이지
    # ========================================

    async def create_page(
        self,
        parent_id: str,
        title: str,
        icon: str | None = None,
        cover_url: str | None = None,
        children: list[dict] | None = None,
    ) -> dict[str, Any]:
        if self.mock_mode:
            return self._mock_page(parent_id, title, icon, cover_url)

        properties = {"title": [{"text": {"content": title}}]}
        page_data: dict[str, Any] = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": properties,
        }
        if icon:
            page_data["icon"] = {"type": "emoji", "emoji": icon}
        if cover_url:
            page_data["cover"] = {"type": "external", "external": {"url": cover_url}}
        if children:
            page_data["children"] = children[:100]

        return await self.rate_limiter.call_with_retry(self._real_client.pages.create, **page_data)

    # ========================================
    # 데이터베이스
    # ========================================

    async def create_database(
        self,
        parent_id: str,
        title: str,
        properties: dict[str, Any],
        is_inline: bool = True,
    ) -> dict[str, Any]:
        if self.mock_mode:
            return self._mock_database(parent_id, title, properties)

        db_data = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "is_inline": is_inline,
            "properties": properties,
        }
        return await self.rate_limiter.call_with_retry(self._real_client.databases.create, **db_data)

    async def get_database(self, database_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": database_id, "properties": {}, "data_sources": [{"id": database_id}]}
        return await self.rate_limiter.call_with_retry(
            self._real_client.databases.retrieve, database_id=database_id
        )

    async def get_data_source_id(self, database_id: str) -> str:
        """DB의 data_source_id를 조회 (Views API에 필요)"""
        db_info = await self.get_database(database_id)
        data_sources = db_info.get("data_sources", [])
        if data_sources:
            return data_sources[0]["id"]
        return database_id

    async def update_database(self, database_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": database_id, **updates}
        return await self.rate_limiter.call_with_retry(
            self._real_client.databases.update, database_id=database_id, **updates
        )

    # ========================================
    # 블록
    # ========================================

    async def add_blocks(self, page_id: str, blocks: list[dict]) -> list[dict]:
        if self.mock_mode:
            return self._mock_blocks(page_id, blocks)

        results = []
        for i in range(0, len(blocks), 100):
            chunk = blocks[i : i + 100]
            resp = await self.rate_limiter.call_with_retry(
                self._real_client.blocks.children.append,
                block_id=page_id,
                children=chunk,
            )
            results.extend(resp.get("results", []))
        return results

    # ========================================
    # DB 아이템
    # ========================================

    async def add_database_item(
        self,
        database_id: str,
        properties: dict[str, Any],
        icon: str | None = None,
        cover_url: str | None = None,
    ) -> dict[str, Any]:
        if self.mock_mode:
            return self._mock_db_item(database_id, properties, icon)

        page_data: dict[str, Any] = {
            "parent": {"type": "database_id", "database_id": database_id},
            "properties": properties,
        }
        if icon:
            page_data["icon"] = {"type": "emoji", "emoji": icon}
        if cover_url:
            page_data["cover"] = {"type": "external", "external": {"url": cover_url}}

        return await self.rate_limiter.call_with_retry(self._real_client.pages.create, **page_data)

    # ========================================
    # Views API (2026-03-19)
    # ========================================

    async def create_view(
        self,
        database_id: str,
        view_type: str,
        title: str = "",
        filters: dict | None = None,
        sorts: list[dict] | None = None,
    ) -> dict[str, Any]:
        """DB에 뷰 생성 (gallery, board, calendar, timeline, list, table)

        핵심: data_source_id는 database_id와 다름!
        DB 생성 후 get_data_source_id()로 조회 필요.
        """
        if self.mock_mode:
            return {"id": self._mock_id(), "type": view_type, "name": title}

        # data_source_id 조회
        data_source_id = await self.get_data_source_id(database_id)

        body: dict[str, Any] = {
            "database_id": database_id,
            "data_source_id": data_source_id,
            "name": title or view_type,
            "type": view_type,
        }
        if filters:
            body["filter"] = filters
        if sorts:
            body["sort"] = sorts

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/views", json=body)
            if resp.status_code >= 400:
                error_body = resp.text[:200]
                print(f"[Views API {resp.status_code}] {view_type}: {error_body}")
                return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}
            return resp.json()
        except Exception as e:
            print(f"[Views API 에러] {view_type}: {str(e)[:100]}")
            return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}

    # ========================================
    # Mock 응답
    # ========================================

    def _mock_id(self) -> str:
        return str(uuid.uuid4()).replace("-", "")

    def _mock_page(self, parent_id: str, title: str, icon: str | None, cover_url: str | None) -> dict[str, Any]:
        page_id = self._mock_id()
        return {
            "id": page_id,
            "object": "page",
            "url": f"https://notion.so/mock-{page_id[:8]}",
            "parent": {"page_id": parent_id},
            "properties": {"title": {"title": [{"text": {"content": title}}]}},
            "icon": {"type": "emoji", "emoji": icon} if icon else None,
            "cover": {"type": "external", "external": {"url": cover_url}} if cover_url else None,
        }

    def _mock_database(self, parent_id: str, title: str, properties: dict) -> dict[str, Any]:
        db_id = self._mock_id()
        return {
            "id": db_id,
            "object": "database",
            "url": f"https://notion.so/mock-db-{db_id[:8]}",
            "parent": {"page_id": parent_id},
            "title": [{"text": {"content": title}}],
            "properties": properties,
            "data_sources": [{"id": self._mock_id(), "name": title}],
        }

    def _mock_blocks(self, page_id: str, blocks: list[dict]) -> list[dict]:
        return [{"id": self._mock_id(), "object": "block", **b} for b in blocks]

    def _mock_db_item(self, database_id: str, properties: dict, icon: str | None) -> dict[str, Any]:
        return {
            "id": self._mock_id(),
            "object": "page",
            "parent": {"database_id": database_id},
            "properties": properties,
            "icon": {"type": "emoji", "emoji": icon} if icon else None,
        }
