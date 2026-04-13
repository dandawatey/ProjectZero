"""JWT auth middleware — PRJ0-28.

Skip list: /health, /api/v1/auth/*
All other /api/v1/* require valid Bearer token.
Sets request.state.user_id + request.state.user_role on success.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.security import decode_access_token
from fastapi import HTTPException

_SKIP_PREFIXES = ("/health", "/api/v1/auth/", "/docs", "/openapi.json", "/redoc")


class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip auth for public paths
        if any(path == p or path.startswith(p) for p in _SKIP_PREFIXES):
            return await call_next(request)

        # Only enforce on /api/v1/* routes
        if not path.startswith("/api/v1/"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=401)

        token = auth_header[7:]
        settings = get_settings()
        try:
            payload = decode_access_token(token, settings.jwt_secret_key, settings.jwt_algorithm)
            request.state.user_id = payload.get("sub")
            request.state.user_role = payload.get("role")
        except HTTPException as e:
            return JSONResponse({"detail": e.detail}, status_code=e.status_code)

        return await call_next(request)
