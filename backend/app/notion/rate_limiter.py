"""Notion API Rate Limiter — 초당 요청 수(timestamp 슬라이딩 윈도우) 페이싱 + 429 재시도(지수 백오프 +jitter, Retry-After).

주의: acquire()는 요청 '개시 시점'을 max_per_second로 페이싱한다(동시 in-flight 요청 수를 잡아두는
방식이 아님). 내부 semaphore는 timestamp 부킹 구간을 직렬화하는 용도이며, 호출자는 acquire() 반환
직후 HTTP 요청을 보낸다. 진짜 동시성 상한이 필요하면 호출부(asyncio.gather)에서 별도 제한할 것.
"""

import asyncio
import logging
import random
import time
from collections import deque
from typing import Any, Callable, Coroutine

logger = logging.getLogger("notionforge.rate_limiter")


def _parse_retry_after(error: Exception) -> float | None:
    """예외에 붙은 응답 헤더에서 Retry-After(초)를 best-effort로 파싱."""
    resp = getattr(error, "response", None)
    headers = getattr(resp, "headers", None) if resp is not None else None
    if not headers:
        return None
    try:
        val = headers.get("Retry-After") or headers.get("retry-after")
        return float(val) if val is not None else None
    except (ValueError, TypeError, AttributeError):
        return None


class RateLimiter:
    def __init__(self, max_per_second: int = 3):
        self.max_per_second = max_per_second
        self._timestamps: deque[float] = deque()
        self._semaphore = asyncio.Semaphore(max_per_second)
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        await self._semaphore.acquire()
        try:
            async with self._lock:
                now = time.monotonic()
                while self._timestamps and self._timestamps[0] <= now - 1.0:
                    self._timestamps.popleft()

                if len(self._timestamps) >= self.max_per_second:
                    wait_time = 1.0 - (now - self._timestamps[0])
                    if wait_time > 0:
                        await asyncio.sleep(wait_time)

                self._timestamps.append(time.monotonic())
        finally:
            self._semaphore.release()

    async def call_with_retry(
        self,
        func: Callable[..., Coroutine[Any, Any, Any]],
        *args: Any,
        max_retries: int = 3,
        **kwargs: Any,
    ) -> Any:
        for attempt in range(max_retries):
            await self.acquire()
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "rate" in error_str.lower():
                    if attempt == max_retries - 1:
                        raise
                    # Retry-After 우선, 없으면 지수 백오프 + jitter (thundering herd 방지)
                    retry_after = _parse_retry_after(e)
                    wait = retry_after if retry_after is not None else (2**attempt) + random.uniform(0, 0.5)
                    logger.info(f"[RateLimiter] 429 감지, {wait:.1f}s 대기 (시도 {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait)
                else:
                    raise
        return None

    async def gather_with_limit(
        self,
        tasks: list[Callable[..., Coroutine[Any, Any, Any]]],
    ) -> list[Any]:
        """Rate limit을 준수하면서 여러 코루틴을 병렬 실행"""

        async def _wrapped(task_fn: Callable[..., Coroutine[Any, Any, Any]]) -> Any:
            await self.acquire()
            return await task_fn()

        return await asyncio.gather(*[_wrapped(t) for t in tasks], return_exceptions=True)
