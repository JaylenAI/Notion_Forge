"""Views API 작업 (2026-03-11+)

10종 뷰: table, board, gallery, calendar, timeline, list, chart, form, map, dashboard
Dashboard 위젯 배치, Form 권한, View Query 지원
"""

import logging
from typing import Any

logger = logging.getLogger("notionforge.notion_client")


class ViewOpsMixin:
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
        configuration: dict | None = None,
    ) -> dict[str, Any]:
        """DB에 뷰 생성 (gallery, board, calendar, timeline, list, table, chart, form, map, dashboard)"""
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
        if configuration:
            body["configuration"] = configuration

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/views", json=body)
            if resp.status_code >= 400:
                error_body = resp.text[:200]
                logger.warning(f"[Views API {resp.status_code}] {view_type}: {error_body}")
                if configuration:
                    logger.warning("[Views API 폴백] configuration 제거 후 재시도")
                    body.pop("configuration", None)
                    await self.rate_limiter.acquire()
                    resp2 = await self._http_client.post("/views", json=body)
                    if resp2.status_code < 400:
                        return resp2.json()
                return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[Views API 에러] {view_type}: {str(e)[:100]}")
            return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}

    async def update_view(self, view_id: str, **kwargs) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": view_id, **kwargs}
        body = {k: v for k, v in kwargs.items() if v is not None}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.patch(f"/views/{view_id}", json=body)
            if resp.status_code >= 400:
                logger.warning(f"[update_view 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": view_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_view 에러] {str(e)[:100]}")
            return {"id": view_id, "fallback": True}

    async def delete_view(self, view_id: str) -> bool:
        if self.mock_mode:
            return True
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.delete(f"/views/{view_id}")
            if resp.status_code >= 400:
                logger.warning(f"[delete_view 에러 {resp.status_code}] {resp.text[:200]}")
                return False
            return True
        except Exception as e:
            logger.warning(f"[delete_view 에러] {str(e)[:100]}")
            return False

    async def list_views(self, database_id: str) -> list[dict]:
        if self.mock_mode:
            return []
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/databases/{database_id}/views")
            if resp.status_code >= 400:
                logger.warning(f"[list_views 에러 {resp.status_code}] {resp.text[:200]}")
                return []
            return resp.json().get("results", [])
        except Exception as e:
            logger.warning(f"[list_views 에러] {str(e)[:100]}")
            return []

    async def get_view(self, view_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": view_id}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/views/{view_id}")
            if resp.status_code >= 400:
                return {"id": view_id}
            return resp.json()
        except Exception as e:
            logger.warning(f"[get_view 에러] {str(e)[:100]}")
            return {"id": view_id}

    async def create_linked_view(
        self,
        source_database_id: str,
        target_page_id: str,
        view_type: str = "table",
        title: str = "",
        filters: dict | None = None,
        sorts: list[dict] | None = None,
        group_by: dict | None = None,
        configuration: dict | None = None,
    ) -> dict[str, Any]:
        """기존 DB를 다른 페이지에 링크드 뷰로 삽입"""
        if self.mock_mode:
            return {"id": self._mock_id(), "type": view_type, "name": title, "linked": True}

        data_source_id = await self.get_data_source_id(source_database_id)

        body: dict[str, Any] = {
            "create_database": {
                "parent": {"type": "page_id", "page_id": target_page_id},
            },
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
        if configuration:
            body["configuration"] = configuration

        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post("/views", json=body)
            if resp.status_code >= 400:
                logger.info(f"[Linked View API {resp.status_code}] {resp.text[:200]}")
                return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[Linked View API 에러] {e}")
            return {"id": self._mock_id(), "type": view_type, "name": title, "fallback": True}

    async def create_dashboard_view(
        self,
        database_id: str,
        title: str = "",
        widgets: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Dashboard 뷰 생성 + 위젯 배치 configuration"""
        configuration = None
        if widgets:
            configuration = {"widgets": widgets}
        return await self.create_view(
            database_id=database_id,
            view_type="dashboard",
            title=title or "Dashboard",
            configuration=configuration,
        )

    async def create_form_view(
        self,
        database_id: str,
        title: str = "",
        submission_permissions: str = "disabled",
        cover_url: str = "",
        description: str = "",
    ) -> dict[str, Any]:
        """Form 뷰 생성 + 제출 권한 설정

        submission_permissions: "disabled" | "by_anyone" | "by_anyone_in_workspace"
        """
        configuration: dict[str, Any] = {}
        if submission_permissions != "disabled":
            configuration["submission_permissions"] = {"type": submission_permissions}
        if cover_url:
            configuration["cover"] = {"type": "external", "external": {"url": cover_url}}
        if description:
            configuration["description"] = description

        return await self.create_view(
            database_id=database_id,
            view_type="form",
            title=title or "Form",
            configuration=configuration if configuration else None,
        )

    async def create_view_query(
        self,
        view_id: str,
        filters: dict | None = None,
        sorts: list[dict] | None = None,
        page_size: int = 50,
    ) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": self._mock_id(), "results": []}
        body: dict[str, Any] = {"page_size": min(page_size, 100)}
        if filters:
            body["filter"] = filters
        if sorts:
            body["sorts"] = sorts
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.post(f"/views/{view_id}/queries", json=body)
            if resp.status_code >= 400:
                logger.warning(f"[view_query 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": self._mock_id(), "results": []}
            return resp.json()
        except Exception as e:
            logger.warning(f"[view_query 에러] {str(e)[:100]}")
            return {"id": self._mock_id(), "results": []}
