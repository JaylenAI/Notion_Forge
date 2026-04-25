"""Page CRUD + archive/restore/lock/move/markdown 작업"""

import logging
from typing import Any

logger = logging.getLogger("notionforge.notion_client")


class PageOpsMixin:
    async def create_page(
        self,
        parent_id: str,
        title: str,
        icon: str | None = None,
        cover_url: str | None = None,
        children: list[dict] | None = None,
        position: str = "",
    ) -> dict[str, Any]:
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
                if "icon.emoji" in error_text and icon:
                    logger.warning(f"[Icon 폴백] 잘못된 이모지 '{icon}' → 아이콘 없이 재시도")
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

    async def get_page(self, page_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": page_id, "object": "page"}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/pages/{page_id}")
            if resp.status_code >= 400:
                return {"id": page_id}
            return resp.json()
        except Exception as e:
            logger.warning(f"[get_page 에러] {str(e)[:100]}")
            return {"id": page_id}

    async def update_page(self, page_id: str, **kwargs) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": page_id, **kwargs}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.patch(f"/pages/{page_id}", json=kwargs)
            if resp.status_code >= 400:
                logger.warning(f"[update_page 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": page_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_page 에러] {str(e)[:100]}")
            return {"id": page_id, "fallback": True}

    async def delete_page(self, page_id: str) -> bool:
        if self.mock_mode:
            return True
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.delete(f"/pages/{page_id}")
            if resp.status_code >= 400:
                logger.warning(f"[delete_page 에러 {resp.status_code}] {resp.text[:200]}")
                return False
            return True
        except Exception as e:
            logger.warning(f"[delete_page 에러] {str(e)[:100]}")
            return False

    async def move_page(self, page_id: str, new_parent_id: str) -> dict:
        if self.mock_mode:
            return {"id": page_id, "parent": {"page_id": new_parent_id}}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(
            f"/pages/{page_id}",
            json={"parent": {"type": "page_id", "page_id": new_parent_id}},
        )
        if resp.status_code >= 400:
            logger.warning(f"[페이지 이동 에러] {resp.text[:200]}")
            return {"id": page_id}
        return resp.json()

    async def archive_page(self, page_id: str) -> dict:
        if self.mock_mode:
            return {"id": page_id, "in_trash": True}
        return await self.rate_limiter.call_with_retry(self._real_client.pages.update, page_id=page_id, in_trash=True)

    async def restore_page(self, page_id: str) -> dict:
        if self.mock_mode:
            return {"id": page_id, "in_trash": False}
        return await self.rate_limiter.call_with_retry(self._real_client.pages.update, page_id=page_id, in_trash=False)

    async def lock_page(self, page_id: str, locked: bool = True) -> dict:
        if self.mock_mode:
            return {"id": page_id, "is_locked": locked}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(f"/pages/{page_id}", json={"is_locked": locked})
        return resp.json()

    async def create_page_markdown(self, parent_id: str, title: str, markdown: str, icon: str | None = None) -> dict:
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
            logger.info(f"[Markdown API {resp.status_code}] {resp.text[:100]}")
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

    async def update_page_content_markdown(self, page_id: str, markdown: str) -> dict:
        if self.mock_mode:
            return {"id": page_id}
        await self.rate_limiter.acquire()
        resp = await self._http_client.patch(
            f"/pages/{page_id}",
            json={"replace_content": {"markdown": markdown}},
        )
        if resp.status_code >= 400:
            logger.warning(f"[마크다운 교체 에러] {resp.text[:200]}")
            return {"id": page_id}
        return resp.json()
