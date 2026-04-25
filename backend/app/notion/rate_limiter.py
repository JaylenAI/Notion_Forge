"""Notion API Rate Limiter: Semaphore 기반 동시 요청 제한 + 지수 백오프"""

import asyncio
import logging
import time
from collections import deque
from typing import Any, Callable, Coroutine

logger = logging.getLogger("notionforge.rate_limiter")


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
                    wait = 2**attempt
                    logger.info(f"[RateLimiter] 429 감지, {wait}s 대기 (시도 {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait)
                    if attempt == max_retries - 1:
                        raise
                else:
                    raise

    async def gather_with_limit(
        self,
        tasks: list[Callable[..., Coroutine[Any, Any, Any]]],
    ) -> list[Any]:
        """Rate limit을 준수하면서 여러 코루틴을 병렬 실행"""

        async def _wrapped(task_fn: Callable[..., Coroutine[Any, Any, Any]]) -> Any:
            await self.acquire()
            return await task_fn()

        return await asyncio.gather(*[_wrapped(t) for t in tasks], return_exceptions=True)
