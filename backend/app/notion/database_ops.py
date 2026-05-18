"""Database CRUD + query + items 작업

DB 생성/수정/아이템 추가: legacy API (2022-06-28) — 속성 정상 처리
DB 쿼리/data_sources/views: 최신 API (2026-03-11)
"""

import logging
from typing import Any

logger = logging.getLogger("notionforge.notion_client")


class DatabaseOpsMixin:
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

        logger.info(f"[DB 생성] '{title}' 속성: {list(properties.keys())}")

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client_legacy.post("/databases", json=db_data)
            if resp.status_code < 400:
                return resp.json()

            error_text = resp.text[:500]
            logger.warning(f"[DB 생성 에러] '{title}' ({resp.status_code}): {error_text}")

            if "validation" in error_text.lower() or "property" in error_text.lower():
                title_prop = {}
                other_props = {}
                for pname, pconfig in properties.items():
                    if isinstance(pconfig, dict) and "title" in pconfig:
                        title_prop[pname] = pconfig
                    else:
                        other_props[pname] = pconfig

                if not title_prop:
                    title_prop = {"이름": {"title": {}}}

                db_data["properties"] = title_prop
                await self.rate_limiter.acquire()
                resp2 = await self._http_client_legacy.post("/databases", json=db_data)
                if resp2.status_code >= 400:
                    raise RuntimeError(f"DB 생성 API 에러 ({resp2.status_code}): {resp2.text[:200]}")

                db = resp2.json()
                db_id = db["id"]
                logger.info(f"[DB 생성] '{title}' title만 생성 성공, 나머지 {len(other_props)}개 속성 개별 추가 시도")

                added = 0
                for pname, pconfig in other_props.items():
                    try:
                        await self.rate_limiter.acquire()
                        patch_resp = await self._http_client_legacy.patch(
                            f"/databases/{db_id}",
                            json={"properties": {pname: pconfig}},
                        )
                        if patch_resp.status_code < 400:
                            added += 1
                        else:
                            logger.warning(f"[DB 속성 추가 실패] {pname}: {patch_resp.text[:100]}")
                    except Exception as e:
                        logger.warning(f"[DB 속성 추가 실패] {pname}: {str(e)[:80]}")

                logger.info(f"[DB 생성] '{title}' 속성 개별 추가: {added}/{len(other_props)}개 성공")
                return await self.get_database(db_id)

            raise RuntimeError(f"DB 생성 API 에러 ({resp.status_code}): {error_text[:200]}")
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"데이터베이스 '{title}' 생성 실패: {e}") from e

    async def get_database(self, database_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": database_id, "properties": {}, "data_sources": [{"id": database_id}]}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/databases/{database_id}")
            if resp.status_code >= 400:
                return {"id": database_id, "properties": {}}
            return resp.json()
        except Exception as e:
            logger.warning(f"[get_database 에러] {str(e)[:100]}")
            return {"id": database_id, "properties": {}}

    async def get_data_source_id(self, database_id: str) -> str:
        db_info = await self.get_database(database_id)
        data_sources = db_info.get("data_sources", [])
        if data_sources:
            return data_sources[0]["id"]
        return database_id

    async def get_data_source(self, data_source_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": data_source_id, "properties": {}}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/data_sources/{data_source_id}")
            if resp.status_code >= 400:
                return {"id": data_source_id, "properties": {}}
            return resp.json()
        except Exception as e:
            logger.warning(f"[get_data_source 에러] {str(e)[:100]}")
            return {"id": data_source_id, "properties": {}}

    async def update_data_source(self, data_source_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": data_source_id, **updates}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.patch(f"/data_sources/{data_source_id}", json=updates)
            if resp.status_code >= 400:
                logger.warning(f"[update_data_source 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": data_source_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_data_source 에러] {str(e)[:100]}")
            return {"id": data_source_id, "fallback": True}

    async def list_data_source_templates(self, data_source_id: str) -> list[dict]:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/data_sources/{data_source_id}/templates")
            if resp.status_code >= 400:
                return []
            return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"[list_templates 에러] {str(e)[:100]}")
            return []

    async def update_database(self, database_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": database_id, **updates}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client_legacy.patch(f"/databases/{database_id}", json=updates)
            if resp.status_code >= 400:
                logger.warning(f"[update_database 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": database_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_database 에러] {str(e)[:100]}")
            return {"id": database_id, "fallback": True}

    async def lock_database(self, database_id: str, locked: bool = True) -> dict:
        if self.mock_mode:
            return {"id": database_id, "is_locked": locked}
        await self.rate_limiter.acquire()
        resp = await self._http_client_legacy.patch(f"/databases/{database_id}", json={"is_locked": locked})
        return resp.json()

    async def add_database_item(
        self,
        database_id: str,
        properties: dict[str, Any],
        icon: str | None = None,
        cover_url: str | None = None,
        template_id: str = "",
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
        if template_id:
            page_data["template"] = {"type": "template_id", "template_id": template_id}

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client_legacy.post("/pages", json=page_data)
            if resp.status_code >= 400:
                error_text = resp.text[:500]
                logger.warning(f"[DB Item 에러 상세] {error_text}")
                logger.info(f"[DB Item 전송 데이터] properties keys: {list(properties.keys())}")
                if "icon.emoji" in error_text and icon:
                    logger.warning(f"[DB Item Icon 폴백] 잘못된 이모지 '{icon}' → 아이콘 없이 재시도")
                    page_data.pop("icon", None)
                    await self.rate_limiter.acquire()
                    resp = await self._http_client_legacy.post("/pages", json=page_data)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"DB 항목 추가 API 에러: {resp.text[:300]}")
                elif "validation" in error_text.lower() or "property" in error_text.lower():
                    retry_props = dict(properties)
                    if "status" in error_text.lower():
                        retry_props = {
                            k: v for k, v in retry_props.items() if not (isinstance(v, dict) and "status" in v)
                        }
                        logger.warning("[DB Item 폴백] status 속성 제거 후 재시도")
                    elif "select" in error_text.lower():
                        retry_props = {
                            k: v for k, v in retry_props.items() if not (isinstance(v, dict) and "select" in v)
                        }
                        logger.warning("[DB Item 폴백] select 속성 제거 후 재시도")
                    else:
                        title_only = {k: v for k, v in retry_props.items() if isinstance(v, dict) and "title" in v}
                        retry_props = title_only if title_only else retry_props
                        logger.warning("[DB Item 폴백] title만으로 재시도")
                    page_data["properties"] = retry_props
                    page_data.pop("icon", None)
                    await self.rate_limiter.acquire()
                    resp = await self._http_client_legacy.post("/pages", json=page_data)
                    if resp.status_code >= 400:
                        raise RuntimeError(f"DB 항목 추가 API 에러 (폴백): {resp.text[:300]}")
                else:
                    raise RuntimeError(f"DB 항목 추가 API 에러: {error_text[:300]}")
            return resp.json()
        except RuntimeError:
            raise
        except Exception as e:
            raise RuntimeError(f"DB 아이템 추가 실패 (db={database_id[:8]}...): {e}") from e

    async def query_database(
        self,
        database_id: str,
        filters: dict | None = None,
        sorts: list[dict] | None = None,
        page_size: int = 100,
        filter_properties: list[str] | None = None,
    ) -> list[dict]:
        if self.mock_mode:
            return []
        body: dict[str, Any] = {"page_size": min(page_size, 100)}
        if filters:
            body["filter"] = filters
        if sorts:
            body["sorts"] = sorts
        if filter_properties:
            body["filter_properties"] = filter_properties

        data_source_id = await self.get_data_source_id(database_id)
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post(f"/data_sources/{data_source_id}/query", json=body)
            if resp.status_code >= 400:
                # 새 API 실패 시 레거시 쿼리 엔드포인트로 폴백
                logger.info("[query_database] 2026-03-11 실패, 레거시 폴백 시도")
                await self.rate_limiter.acquire()
                resp = await self._http_client_legacy.post(f"/databases/{database_id}/query", json=body)
                if resp.status_code >= 400:
                    logger.warning(f"[query_database 에러 {resp.status_code}] {resp.text[:200]}")
                    return []
            data = resp.json()
            request_status = data.get("request_status", {})
            if request_status.get("type") == "incomplete":
                logger.info(f"[query 부분 결과] reason: {request_status.get('incomplete_reason', 'unknown')}")
            return data.get("results", [])
        except Exception as e:
            logger.warning(f"[query_database 에러] {str(e)[:100]}")
            return []
