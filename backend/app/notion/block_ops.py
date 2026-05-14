"""Block CRUD 작업 (API 2026-03-11: position 객체 — start/end/after_block)"""

import logging
from typing import Any

logger = logging.getLogger("notionforge.notion_client")


class BlockOpsMixin:
    async def add_blocks(
        self,
        page_id: str,
        blocks: list[dict],
        after_block_id: str = "",
        position_type: str = "",
    ) -> list[dict]:
        if self.mock_mode:
            return self._mock_blocks(page_id, blocks)

        try:
            results = []
            for i in range(0, len(blocks), 100):
                chunk = blocks[i : i + 100]
                body: dict[str, Any] = {"children": chunk}
                if after_block_id:
                    body["position"] = {"type": "after_block", "after_block": {"id": after_block_id}}
                elif position_type in ("start", "end"):
                    body["position"] = {"type": position_type}

                await self.rate_limiter.acquire()
                resp = await self._http_client.patch(
                    f"/blocks/{page_id}/children",
                    json=body,
                )
                if resp.status_code >= 400:
                    raise RuntimeError(f"블록 추가 API 에러: {resp.text[:200]}")
                data = resp.json()
                results.extend(data.get("results", []))
                if results:
                    after_block_id = results[-1]["id"]
            return results
        except Exception as e:
            raise RuntimeError(f"블록 추가 실패 (page={page_id[:8]}...): {e}") from e

    async def get_block(self, block_id: str) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": block_id, "type": "paragraph"}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.get(f"/blocks/{block_id}")
            if resp.status_code >= 400:
                return {"id": block_id}
            return resp.json()
        except Exception as e:
            logger.warning(f"[get_block 에러] {str(e)[:100]}")
            return {"id": block_id}

    async def get_block_children(self, block_id: str, page_size: int = 100) -> list[dict]:
        if self.mock_mode:
            return []
        all_children: list[dict] = []
        start_cursor = None
        while True:
            await self.rate_limiter.acquire()
            try:
                params: dict[str, Any] = {"page_size": min(page_size, 100)}
                if start_cursor:
                    params["start_cursor"] = start_cursor
                resp = await self._http_client.get(
                    f"/blocks/{block_id}/children",
                    params=params,
                )
                if resp.status_code >= 400:
                    break
                data = resp.json()
                all_children.extend(data.get("results", []))
                if not data.get("has_more"):
                    break
                start_cursor = data.get("next_cursor")
            except Exception as e:
                logger.warning(f"[get_block_children 에러] {str(e)[:100]}")
                break
        return all_children

    async def update_block(self, block_id: str, block_data: dict[str, Any]) -> dict[str, Any]:
        if self.mock_mode:
            return {"id": block_id, **block_data}
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.patch(f"/blocks/{block_id}", json=block_data)
            if resp.status_code >= 400:
                logger.warning(f"[update_block 에러 {resp.status_code}] {resp.text[:200]}")
                return {"id": block_id, "fallback": True}
            return resp.json()
        except Exception as e:
            logger.warning(f"[update_block 에러] {str(e)[:100]}")
            return {"id": block_id, "fallback": True}

    async def delete_block(self, block_id: str) -> bool:
        if self.mock_mode:
            return True
        await self.rate_limiter.acquire()
        try:
            resp = await self._http_client.delete(f"/blocks/{block_id}")
            if resp.status_code >= 400:
                logger.warning(f"[delete_block 에러 {resp.status_code}] {resp.text[:200]}")
                return False
            return True
        except Exception as e:
            logger.warning(f"[delete_block 에러] {str(e)[:100]}")
            return False
