"""Notion API Client: 실제 API + Mock 모드 지원

API Version: 2026-03-11 (최신)
- 페이지/DB/블록 CRUD (in_trash, position 객체)
- Data Sources API (multi-source DB)
- Views API (10종: table, board, gallery, calendar, timeline, list, chart, form, map, dashboard)
- Markdown Content API (생성/읽기/수정)
- File Upload / Comments / Custom Emoji / Search / Users
- Workers API (Sync/Tool/Webhook) + External Agents API
"""

import logging
import uuid
from typing import Any

import httpx

from app.config import settings
from app.notion.block_ops import BlockOpsMixin
from app.notion.database_ops import DatabaseOpsMixin
from app.notion.page_ops import PageOpsMixin
from app.notion.rate_limiter import RateLimiter
from app.notion.view_ops import ViewOpsMixin
from app.notion.workers import WorkerOpsMixin

logger = logging.getLogger("notionforge.notion_client")

NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2026-03-11"


class NotionClient(PageOpsMixin, DatabaseOpsMixin, BlockOpsMixin, ViewOpsMixin, WorkerOpsMixin):
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

    async def close(self):
        if self._http_client:
            await self._http_client.aclose()

    # ========================================
    # Search API
    # ========================================

    async def search(self, query: str = "", filter_type: str = "") -> dict:
        if self.mock_mode:
            return {"results": []}
        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if filter_type:
            body["filter"] = {"value": filter_type, "property": "object"}
        return await self.rate_limiter.call_with_retry(self._real_client.search, **body)

    # ========================================
    # Users API
    # ========================================

    async def list_users(self) -> list:
        if self.mock_mode:
            return []
        result = await self.rate_limiter.call_with_retry(self._real_client.users.list)
        return result.get("results", [])

    async def get_user(self, user_id: str) -> dict:
        if self.mock_mode:
            return {"id": user_id}
        return await self.rate_limiter.call_with_retry(self._real_client.users.retrieve, user_id=user_id)

    # ========================================
    # Comments API
    # ========================================

    async def add_comment(
        self,
        text: str = "",
        markdown: str = "",
        page_id: str = "",
        block_id: str = "",
        discussion_id: str = "",
        display_name: str = "",
    ) -> dict:
        if self.mock_mode:
            return {"id": self._mock_id()}

        body: dict[str, Any] = {}
        if markdown:
            body["markdown"] = markdown
        elif text:
            from app.notion.block_builder import rich_text

            body["rich_text"] = rich_text(text)

        if discussion_id:
            body["discussion_id"] = discussion_id
        elif block_id:
            body["parent"] = {"block_id": block_id}
        elif page_id:
            body["parent"] = {"page_id": page_id}

        if display_name:
            body["display_name"] = {"type": "custom", "custom": {"name": display_name}}

        await self.rate_limiter.acquire()
        resp = await self._http_client.post("/comments", json=body)
        if resp.status_code >= 400:
            logger.warning(f"[add_comment 에러] {resp.text[:200]}")
            return {"id": self._mock_id()}
        return resp.json()

    async def update_comment(self, comment_id: str, text: str = "", markdown: str = "") -> dict:
        if self.mock_mode:
            return {"id": comment_id}
        body: dict[str, Any] = {}
        if markdown:
            body["markdown"] = markdown
        elif text:
            from app.notion.block_builder import rich_text

            body["rich_text"] = rich_text(text)
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(f"/comments/{comment_id}", json=body)
        if resp.status_code >= 400:
            logger.warning(f"[update_comment 에러] {resp.text[:200]}")
            return {"id": comment_id}
        return resp.json()

    async def delete_comment(self, comment_id: str) -> bool:
        if self.mock_mode:
            return True
        await self.rate_limiter.acquire()
        resp = await self._http_client.delete(f"/comments/{comment_id}")
        if resp.status_code >= 400:
            logger.warning(f"[delete_comment 에러] {resp.text[:200]}")
            return False
        return True

    async def get_comments(self, block_id: str) -> list:
        if self.mock_mode:
            return []
        result = await self.rate_limiter.call_with_retry(self._real_client.comments.list, block_id=block_id)
        return result.get("results", [])

    # ========================================
    # File Upload API
    # ========================================

    async def create_file_upload(self, filename: str, content_type: str, file_bytes: bytes) -> dict:
        if self.mock_mode:
            return {"id": self._mock_id(), "status": "uploaded", "filename": filename}
        await self.rate_limiter.acquire()
        try:
            create_resp = await self._http_client.post("/file_uploads", json={})
            if create_resp.status_code >= 400:
                logger.warning(f"[file_upload 생성 에러] {create_resp.text[:200]}")
                return {"id": self._mock_id(), "status": "failed"}
            upload = create_resp.json()
            upload_id = upload["id"]

            await self.rate_limiter.acquire()
            import io

            files = {"file": (filename, io.BytesIO(file_bytes), content_type)}
            send_resp = await self._http_client.post(
                f"/file_uploads/{upload_id}/send",
                files=files,
                data={"part_number": "1"},
                headers={"Content-Type": None},
            )
            if send_resp.status_code >= 400:
                logger.warning(f"[file_upload 전송 에러] {send_resp.text[:200]}")
                return {"id": upload_id, "status": "failed"}
            return send_resp.json()
        except Exception as e:
            logger.warning(f"[file_upload 에러] {str(e)[:100]}")
            return {"id": self._mock_id(), "status": "failed"}

    async def get_file_upload(self, upload_id: str) -> dict:
        if self.mock_mode:
            return {"id": upload_id, "status": "uploaded"}
        await self.rate_limiter.acquire()
        resp = await self._http_client.get(f"/file_uploads/{upload_id}")
        if resp.status_code >= 400:
            return {"id": upload_id}
        return resp.json()

    async def list_file_uploads(self) -> list[dict]:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        resp = await self._http_client.get("/file_uploads")
        if resp.status_code >= 400:
            return []
        return resp.json().get("results", [])

    # ========================================
    # Meeting Notes Query API
    # ========================================

    async def query_meeting_notes(self, filters: dict | None = None, page_size: int = 25) -> list[dict]:
        if self.mock_mode:
            return []
        body: dict[str, Any] = {"page_size": min(page_size, 100)}
        if filters:
            body["filter"] = filters
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/blocks/meeting_notes/query", json=body)
            if resp.status_code >= 400:
                return []
            return resp.json().get("results", [])
        except Exception:
            return []

    # ========================================
    # Custom Emoji API
    # ========================================

    async def list_custom_emojis(self) -> list:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get("/custom_emojis")
            if resp.status_code >= 400:
                return []
            return resp.json().get("results", [])
        except Exception:
            return []

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
