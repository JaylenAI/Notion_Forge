"""보안 미들웨어 — Rate Limiting + Request ID + Error Sanitization"""

import logging
import time
import uuid
from collections import defaultdict

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger("notionforge.middleware")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP 기반 슬라이딩 윈도우 Rate Limiter"""

    def __init__(self, app, rpm: int = 60, burst: int = 10):
        super().__init__(app)
        self.rpm = rpm
        self.burst = burst
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _get_client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _cleanup_old_entries(self) -> None:
        now = time.time()
        if now - self._last_cleanup < 60:
            return
        self._last_cleanup = now
        cutoff = now - 60
        expired_ips = []
        for ip, timestamps in self._requests.items():
            self._requests[ip] = [t for t in timestamps if t > cutoff]
            if not self._requests[ip]:
                expired_ips.append(ip)
        for ip in expired_ips:
            del self._requests[ip]

    def _is_exempt(self, path: str) -> bool:
        return path.startswith("/health") or path in ("/docs", "/redoc", "/openapi.json", "/metrics")

    async def dispatch(self, request: Request, call_next) -> Response:
        if self._is_exempt(request.url.path):
            return await call_next(request)

        self._cleanup_old_entries()

        client_ip = self._get_client_ip(request)
        now = time.time()
        window_start = now - 60

        timestamps = self._requests[client_ip]
        timestamps = [t for t in timestamps if t > window_start]
        self._requests[client_ip] = timestamps

        if len(timestamps) >= self.rpm:
            retry_after = int(60 - (now - timestamps[0]))
            return JSONResponse(
                status_code=429,
                content={"error": "요청 한도 초과. 잠시 후 다시 시도해주세요.", "retry_after": max(retry_after, 1)},
                headers={"Retry-After": str(max(retry_after, 1))},
            )

        timestamps.append(now)
        self._requests[client_ip] = timestamps

        return await call_next(request)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """X-Request-ID 헤더 추가"""

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4())[:12])
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 응답 헤더 자동 설정"""

    # Swagger/ReDoc는 CDN 자산을 로드하므로 CSP 적용 제외
    _CSP_EXEMPT = ("/docs", "/redoc", "/openapi.json")

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if not request.url.path.startswith(self._CSP_EXEMPT):
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; img-src 'self' data: https:; "
                "style-src 'self' 'unsafe-inline'; script-src 'self'; "
                "connect-src 'self' ws: wss:; frame-ancestors 'none'; base-uri 'self'"
            )
        return response


def sanitize_error(error: Exception, include_details: bool = False) -> str:
    """에러 메시지 Sanitization — 프로덕션에서 내부 정보 숨김"""
    error_str = str(error)

    if include_details:
        return error_str[:500]

    sensitive_patterns = ["Traceback", 'File "/', "line ", "sqlalchemy", "psycopg", "Internal Server"]
    for pattern in sensitive_patterns:
        if pattern.lower() in error_str.lower():
            return "처리 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    if len(error_str) > 200:
        return error_str[:200]

    return error_str
