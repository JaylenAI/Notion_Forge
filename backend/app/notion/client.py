"""Notion API Client: 실제 API + Mock 모드 지원

지원 기능:
- 페이지/DB/블록 CRUD
- Views API (갤러리, 캘린더, 칸반 등) — 2026-03-19
- Tab 블록 — 2026-03-25
- Status 속성 쓰기 — 2026-03-19
- Search / Users / Comments / Archive / Lock / Markdown / Custom Emoji — 2026-03-27
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
            # 2025-09-03 버전 (Views API 등)
            self._http_client = httpx.AsyncClient(
                base_url=NOTION_API_BASE,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": NOTION_VERSION,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
            # 2022-06-28 버전 (DB 생성 시 속성이 정상 동작)
            self._http_legacy = httpx.AsyncClient(
                base_url=NOTION_API_BASE,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Notion-Version": "2022-06-28",
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
        position: str = "",
    ) -> dict[str, Any]:
        """페이지 생성. position: "page_end" | "page_start" | "" (기본 위치)"""
        if self.mock_mode:
            return self._mock_page(parent_id, title, icon, cover_url)

        body: dict[str, Any] = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": {"title": [{"text": {"content": title}}]},
        }
        if icon:
            body["icon"] = {"type": "emoji", "emoji": icon}
        if cover_url:
            body["cover"] = {"type": "external", "external": {"url": cover_url}}
        if children:
            body["children"] = children[:100]
        if position:
            body["position"] = {"type": position}

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/pages", json=body)
            if resp.status_code >= 400:
                error_text = resp.text[:300]
                # 이모지 에러 시 아이콘 없이 재시도
                if "icon.emoji" in error_text and icon:
                    print(f"[Icon 폴백] 잘못된 이모지 '{icon}' → 아이콘 없이 재시도")
                    body.pop("icon", None)
                    await self.rate_limiter.acquire()
                    resp = await self._http_client.post("/pages", json=body)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"페이지 '{title}' 생성 실패: {resp.text[:200]}")
                else:
                    raise RuntimeError(f"페이지 '{title}' 생성 실패: {error_text}")
            return resp.json()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"페이지 '{title}' 생성 실패: {e}") from e

    # ========================================
    # 데이터베이스
    # ========================================

    async def create_database(
        self,
        parent_id: str,
        title: str,
        properties: dict[str, Any],
        is_inline: bool = True,
        description: str = "",
        icon: str | None = None,
        cover_url: str | None = None,
    ) -> dict[str, Any]:
        if self.mock_mode:
            return self._mock_database(parent_id, title, properties)

        db_data: dict[str, Any] = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "title": [{"type": "text", "text": {"content": title}}],
            "is_inline": is_inline,
            "properties": properties,
        }
        if description:
            db_data["description"] = [{"type": "text", "text": {"content": description}}]
        if icon:
            db_data["icon"] = {"type": "emoji", "emoji": icon}
        if cover_url:
            db_data["cover"] = {"type": "external", "external": {"url": cover_url}}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_legacy.post("/databases", json=db_data)
            if resp.status_code >= 400:
                error_text = resp.text[:500]
                print(f"[DB 생성 에러 상세] {error_text}")
                # 속성 문제로 실패 시, 기본 속성만으로 재시도
                if "validation" in error_text.lower() or "property" in error_text.lower():
                    print("[DB 생성] 속성 문제 → 기본 속성(title만)으로 재시도")
                    db_data["properties"] = {"이름": {"title": {}}}
                    await self.rate_limiter.acquire()
                    resp2 = await self._http_legacy.post("/databases", json=db_data)
                    if resp2.status_code < 400:
                        print("[DB 생성] 기본 속성으로 재시도 성공")
                        return resp2.json()
                raise RuntimeError(f"DB 생성 API 에러 ({resp.status_code}): {error_text[:200]}")
            return resp.json()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"데이터베이스 '{title}' 생성 실패: {e}") from e

    async def get_database(self, database_id: str) -> dict[str, Any]:
        """DB 정보 조회 (Legacy API — properties 포함)"""
        if self.mock_mode:
            return {"id": database_id, "properties": {}, "data_sources": [{"id": database_id}]}
        # Legacy API로 조회 (2022-06-28 — properties 정상 반환)
        await self.rate_limiter.acquire()
        resp = await self._http_legacy.get(f"/databases/{database_id}")
        if resp.status_code >= 400:
            return {"id": database_id, "properties": {}}
        legacy_data = resp.json()
        # data_sources는 최신 API에서만 반환되므로 별도 조회
        try:
            await self.rate_limiter.acquire()
            new_resp = await self._http_client.get(f"/databases/{database_id}")
            if new_resp.status_code == 200:
                new_data = new_resp.json()
                legacy_data["data_sources"] = new_data.get("data_sources", [])
        except Exception:
            pass
        return legacy_data

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

    async def add_blocks(
        self,
        page_id: str,
        blocks: list[dict],
        after_block_id: str = "",
    ) -> list[dict]:
        """블록 추가. after_block_id 지정 시 해당 블록 뒤에 삽입."""
        if self.mock_mode:
            return self._mock_blocks(page_id, blocks)

        try:
            results = []
            for i in range(0, len(blocks), 100):
                chunk = blocks[i : i + 100]
                # position 파라미터로 삽입 위치 지정 (2025-09-03+)
                body: dict[str, Any] = {"children": chunk}
                if after_block_id:
                    body["position"] = {"type": "after_block", "after_block": {"id": after_block_id}}

                await self.rate_limiter.acquire()
                resp = await self._http_client.patch(
                    f"/blocks/{page_id}/children",
                    json=body,
                )
                if resp.status_code >= 400:
                    raise RuntimeError(f"블록 추가 API 에러: {resp.text[:200]}")
                data = resp.json()
                results.extend(data.get("results", []))
                # 다음 chunk는 마지막 블록 뒤에 삽입
                if results:
                    after_block_id = results[-1]["id"]
            return results
        except Exception as e:
            raise RuntimeError(f"블록 추가 실패 (page={page_id[:8]}...): {e}") from e

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
            "parent": {"database_id": database_id},
            "properties": properties,
        }
        if icon:
            page_data["icon"] = {"type": "emoji", "emoji": icon}
        if cover_url:
            page_data["cover"] = {"type": "external", "external": {"url": cover_url}}

        # Legacy API로 호출 (속성 호환성)
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_legacy.post("/pages", json=page_data)
            if resp.status_code >= 400:
                error_text = resp.text[:500]
                print(f"[DB Item 에러 상세] {error_text}")
                print(f"[DB Item 전송 데이터] properties keys: {list(properties.keys())}")
                # 이모지 에러 시 아이콘 없이 재시도
                if "icon.emoji" in error_text and icon:
                    print(f"[DB Item Icon 폴백] 잘못된 이모지 '{icon}' → 아이콘 없이 재시도")
                    page_data.pop("icon", None)
                    await self.rate_limiter.acquire()
                    resp = await self._http_legacy.post("/pages", json=page_data)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"DB 항목 추가 API 에러: {resp.text[:300]}")
                # 속성 에러 시 문제 속성 제거 후 재시도
                elif "validation" in error_text.lower() or "property" in error_text.lower():
                    # 에러 메시지에서 문제 속성 타입 추출 (status, select 등)
                    retry_props = dict(properties)
                    if "status" in error_text.lower():
                        retry_props = {k: v for k, v in retry_props.items() if not (isinstance(v, dict) and "status" in v)}
                        print(f"[DB Item 폴백] status 속성 제거 후 재시도")
                    elif "select" in error_text.lower():
                        retry_props = {k: v for k, v in retry_props.items() if not (isinstance(v, dict) and "select" in v)}
                        print(f"[DB Item 폴백] select 속성 제거 후 재시도")
                    else:
                        # 알 수 없는 속성 에러 → title만 남기기
                        title_only = {k: v for k, v in retry_props.items() if isinstance(v, dict) and "title" in v}
                        retry_props = title_only if title_only else retry_props
                        print(f"[DB Item 폴백] title만으로 재시도")
                    page_data["properties"] = retry_props
                    page_data.pop("icon", None)
                    await self.rate_limiter.acquire()
                    resp = await self._http_legacy.post("/pages", json=page_data)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"DB 항목 추가 API 에러 (폴백): {resp.text[:300]}")
                else:
                    raise RuntimeError(f"DB 항목 추가 API 에러: {error_text[:300]}")
            return resp.json()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"DB 아이템 추가 실패 (db={database_id[:8]}...): {e}") from e

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
        group_by: dict | None = None,
        sub_group_by: dict | None = None,
        quick_filters: dict | None = None,
        properties: dict | None = None,
        position: str = "",
    ) -> dict[str, Any]:
        """DB에 뷰 생성 (gallery, board, calendar, timeline, list, table, chart, form, map, dashboard)

        핵심: data_source_id는 database_id와 다름!
        DB 생성 후 get_data_source_id()로 조회 필요.

        group_by: Board/Timeline 그룹핑 (e.g., {"property": "상태"})
        sub_group_by: 2차 그룹핑
        quick_filters: 빠른 필터 (필터바에 표시)
        properties: 속성 표시/숨김 설정
        position: "start" | "end" | "" (뷰 순서)
        """
        if self.mock_mode:
            return {"id": self._mock_id(), "type": view_type, "name": title}

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
        if group_by:
            body["group_by"] = group_by
        if sub_group_by:
            body["sub_group_by"] = sub_group_by
        if quick_filters:
            body["quick_filters"] = quick_filters
        if properties:
            body["properties"] = properties
        if position:
            body["position"] = {"type": position}

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
    # Search API
    # ========================================

    async def search(self, query: str = "", filter_type: str = "") -> dict:
        """Search workspace. filter_type: 'page' or 'database'"""
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
        text: str,
        page_id: str = "",
        block_id: str = "",
        discussion_id: str = "",
    ) -> dict:
        """댓글 추가 — 페이지/블록/디스커션 스레드 지원

        page_id: 페이지 레벨 댓글 (새 디스커션 시작)
        block_id: 블록 레벨 댓글 (새 디스커션 시작)
        discussion_id: 기존 디스커션에 답글
        """
        if self.mock_mode:
            return {"id": self._mock_id()}
        from app.notion.block_builder import rich_text

        kwargs: dict[str, Any] = {"rich_text": rich_text(text)}
        if discussion_id:
            kwargs["discussion_id"] = discussion_id
        elif block_id:
            kwargs["parent"] = {"block_id": block_id}
        elif page_id:
            kwargs["parent"] = {"page_id": page_id}

        return await self.rate_limiter.call_with_retry(
            self._real_client.comments.create, **kwargs
        )

    async def get_comments(self, block_id: str) -> list:
        if self.mock_mode:
            return []
        result = await self.rate_limiter.call_with_retry(
            self._real_client.comments.list, block_id=block_id
        )
        return result.get("results", [])

    # ========================================
    # Page operations (archive / restore / lock / move)
    # ========================================

    async def move_page(self, page_id: str, new_parent_id: str) -> dict:
        """페이지를 다른 부모 페이지로 이동 (2026-01-15+)"""
        if self.mock_mode:
            return {"id": page_id, "parent": {"page_id": new_parent_id}}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(
            f"/pages/{page_id}",
            json={"parent": {"type": "page_id", "page_id": new_parent_id}},
        )
        if resp.status_code >= 400:
            print(f"[페이지 이동 에러] {resp.text[:200]}")
            return {"id": page_id}
        return resp.json()

    async def update_page_content_markdown(self, page_id: str, markdown: str) -> dict:
        """기존 페이지의 마크다운 콘텐츠 교체 (2026-03-11+)"""
        if self.mock_mode:
            return {"id": page_id}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(
            f"/pages/{page_id}",
            json={"replace_content": {"markdown": markdown}},
        )
        if resp.status_code >= 400:
            print(f"[마크다운 교체 에러] {resp.text[:200]}")
            return {"id": page_id}
        return resp.json()

    async def archive_page(self, page_id: str) -> dict:
        if self.mock_mode:
            return {"id": page_id, "in_trash": True}
        return await self.rate_limiter.call_with_retry(
            self._real_client.pages.update, page_id=page_id, in_trash=True
        )

    async def restore_page(self, page_id: str) -> dict:
        if self.mock_mode:
            return {"id": page_id, "in_trash": False}
        return await self.rate_limiter.call_with_retry(
            self._real_client.pages.update, page_id=page_id, in_trash=False
        )

    async def lock_page(self, page_id: str, locked: bool = True) -> dict:
        if self.mock_mode:
            return {"id": page_id, "is_locked": locked}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(f"/pages/{page_id}", json={"is_locked": locked})
        return resp.json()

    async def lock_database(self, database_id: str, locked: bool = True) -> dict:
        if self.mock_mode:
            return {"id": database_id, "is_locked": locked}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(f"/databases/{database_id}", json={"is_locked": locked})
        return resp.json()

    # ========================================
    # Markdown API (httpx — SDK 미지원)
    # ========================================

    async def create_page_markdown(
        self, parent_id: str, title: str, markdown: str, icon: str | None = None
    ) -> dict:
        if self.mock_mode:
            return self._mock_page(parent_id, title, icon, None)
        body: dict[str, Any] = {
            "parent": {"type": "page_id", "page_id": parent_id},
            "properties": {"title": [{"text": {"content": title}}]},
            "markdown": markdown,
        }
        if icon:
            body["icon"] = {"type": "emoji", "emoji": icon}
        await self.rate_limiter.acquire()
        resp = await self._http_client.post("/pages", json=body)
        if resp.status_code >= 400:
            print(f"[Markdown API {resp.status_code}] {resp.text[:100]}")
            return self._mock_page(parent_id, title, icon, None)
        return resp.json()

    async def get_page_markdown(self, page_id: str) -> str:
        if self.mock_mode:
            return ""
        await self.rate_limiter.acquire()
        resp = await self._http_client.get(f"/pages/{page_id}/markdown")
        if resp.status_code >= 400:
            return ""
        data = resp.json()
        return data.get("markdown", "")

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
    # Linked Database View (Views API)
    # ========================================

    async def create_linked_view(
        self,
        source_database_id: str,
        target_page_id: str,
        view_type: str = "table",
        title: str = "",
        filters: dict | None = None,
        sorts: list[dict] | None = None,
    ) -> dict[str, Any]:
        """기존 DB를 다른 페이지에 링크드 뷰로 삽입 (Views API create_database)

        공식 API — POST /v1/views with create_database parameter.
        source DB를 target 페이지에 링크드 뷰로 보여줌 (복사 아님).
        """
        if self.mock_mode:
            return {"id": self._mock_id(), "type": view_type, "name": title, "linked": True}

        data_source_id = await self.get_data_source_id(source_database_id)

        body: dict[str, Any] = {
            "create_database": {
                "parent": {
                    "type": "page_id",
                    "page_id": target_page_id,
                },
            },
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
                print(f"[Linked View API {resp.status_code}] {resp.text[:200]}")
                return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}
            return resp.json()
        except Exception as e:
            print(f"[Linked View API 에러] {e}")
            return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}

    # ========================================
    # Page Full Width (Internal API)
    # ========================================

    async def set_page_full_width(
        self,
        page_id: str,
        full_width: bool = True,
        small_text: bool = False,
        token_v2: str = "",
    ) -> bool:
        """페이지를 전체 너비로 설정 (Notion Internal API)

        공식 API에서 지원하지 않는 기능.
        Notion 내부 API (submitTransaction)를 사용하며,
        token_v2 브라우저 쿠키가 필요함.

        token_v2 획득 방법:
        1. 브라우저에서 notion.so 로그인
        2. 개발자도구 (F12) → Application → Cookies → notion.so
        3. token_v2 값 복사
        """
        if self.mock_mode:
            return True

        t2 = token_v2 or settings.notion_token_v2
        if not t2:
            print("[Full Width] token_v2가 없어서 전체 너비를 설정할 수 없습니다.")
            return False

        # page_id에서 하이픈 제거 (내부 API는 하이픈 없는 UUID 사용)
        clean_id = page_id.replace("-", "")

        payload = {
            "operations": [
                {
                    "id": clean_id,
                    "path": ["format"],
                    "args": {
                        "page_full_width": full_width,
                        "page_small_text": small_text,
                    },
                    "command": "update",
                    "table": "block",
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://www.notion.so/api/v3/submitTransaction",
                    json=payload,
                    headers={
                        "Cookie": f"token_v2={t2}",
                        "Content-Type": "application/json",
                    },
                )
                if resp.status_code == 200:
                    print(f"[Full Width] 페이지 전체 너비 설정 완료: {page_id[:8]}...")
                    return True
                print(f"[Full Width] 실패 ({resp.status_code}): {resp.text[:200]}")
                return False
        except Exception as e:
            print(f"[Full Width] 에러: {e}")
            return False

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
