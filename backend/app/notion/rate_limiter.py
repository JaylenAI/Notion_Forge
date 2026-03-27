"""Notion API Rate Limiter: 3 req/s + 지수 백오프"""

import asyncio
import time
from collections import deque
from typing import Any, Callable, Coroutine


class RateLimiter:
    def __init__(self, max_per_second: int = 3):
        self.max_per_second = max_per_second
        self._timestamps: deque[float] = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            while self._timestamps and self._timestamps[0] <= now - 1.0:
                self._timestamps.popleft()

            if len(self._timestamps) >= self.max_per_second:
                wait_time = 1.0 - (now - self._timestamps[0])
                if wait_time > 0:
                    await asyncio.sleep(wait_time)

            self._timestamps.append(time.monotonic())

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
                    await asyncio.sleep(wait)
                    if attempt == max_retries - 1:
                        raise
                else:
                    raise
