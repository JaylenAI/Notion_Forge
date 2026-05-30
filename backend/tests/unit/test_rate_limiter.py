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


class _FakeResp:
    def __init__(self, retry_after):
        self.headers = {"Retry-After": retry_after}


class _RateError(Exception):
    def __init__(self, msg, retry_after=None):
        super().__init__(msg)
        self.response = _FakeResp(retry_after) if retry_after is not None else None


class TestRetryAfterAndJitter:
    async def test_retry_after_honored(self, monkeypatch):
        from app.notion.rate_limiter import RateLimiter

        rl = RateLimiter(max_per_second=10)
        slept = []

        async def _sleep(s):
            slept.append(s)

        monkeypatch.setattr("asyncio.sleep", _sleep)
        attempts = 0

        async def fn():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise _RateError("429 rate limited", retry_after="0.05")
            return "ok"

        result = await rl.call_with_retry(fn, max_retries=3)
        assert result == "ok"
        assert 0.05 in slept, f"Retry-After가 적용되지 않음: {slept}"

    async def test_backoff_has_jitter(self, monkeypatch):
        from app.notion.rate_limiter import RateLimiter

        rl = RateLimiter(max_per_second=10)
        slept = []

        async def _sleep(s):
            slept.append(s)

        monkeypatch.setattr("asyncio.sleep", _sleep)
        attempts = 0

        async def fn():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise _RateError("429")  # Retry-After 없음 → 지수+jitter
            return "ok"

        await rl.call_with_retry(fn, max_retries=3)
        # attempt 0: 2**0 + jitter(0~0.5) = [1.0, 1.5)
        assert slept and 1.0 <= slept[0] < 1.5, f"jitter 범위 벗어남: {slept}"
