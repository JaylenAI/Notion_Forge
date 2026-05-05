"""Rate Limiter 테스트"""

import pytest

from app.notion.rate_limiter import RateLimiter


class TestRateLimiter:
    async def test_acquire_basic(self):
        rl = RateLimiter(max_per_second=5)
        await rl.acquire()

    async def test_acquire_respects_limit(self):
        rl = RateLimiter(max_per_second=2)
        await rl.acquire()
        await rl.acquire()

    async def test_call_with_retry_success(self):
        rl = RateLimiter(max_per_second=5)
        called = 0

        async def fn():
            nonlocal called
            called += 1
            return "ok"

        result = await rl.call_with_retry(fn)
        assert result == "ok"
        assert called == 1

    async def test_call_with_retry_rate_limit(self):
        rl = RateLimiter(max_per_second=5)
        attempts = 0

        async def fn():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise Exception("429 Too Many Requests")
            return "recovered"

        result = await rl.call_with_retry(fn, max_retries=3)
        assert result == "recovered"
        assert attempts == 2

    async def test_call_with_retry_non_rate_error(self):
        rl = RateLimiter(max_per_second=5)

        async def fn():
            raise ValueError("bad input")

        with pytest.raises(ValueError, match="bad input"):
            await rl.call_with_retry(fn)

    async def test_call_with_retry_exhausted(self):
        rl = RateLimiter(max_per_second=5)

        async def fn():
            raise Exception("rate limit exceeded")

        with pytest.raises(Exception, match="rate limit"):
            await rl.call_with_retry(fn, max_retries=2)

    async def test_gather_with_limit(self):
        rl = RateLimiter(max_per_second=5)
        results = []

        async def task1():
            results.append(1)
            return 1

        async def task2():
            results.append(2)
            return 2

        out = await rl.gather_with_limit([task1, task2])
        assert len(out) == 2
        assert set(results) == {1, 2}

    async def test_gather_with_exception(self):
        rl = RateLimiter(max_per_second=5)

        async def ok_task():
            return "ok"

        async def bad_task():
            raise ValueError("fail")

        out = await rl.gather_with_limit([ok_task, bad_task])
        assert out[0] == "ok"
        assert isinstance(out[1], ValueError)
