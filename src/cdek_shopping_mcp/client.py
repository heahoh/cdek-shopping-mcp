"""HTTP client for the cdek.shopping storefront ("front-controller") API."""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.cdek.shopping/front-controller/v1"
APP_NAME = "ecommerce-mcp"
DEFAULT_MAX_RPS = 5.0


class RateLimiter:
    """Caps requests to at most `rate` per second, spacing calls evenly.

    cdek.shopping asked that agents never exceed 5 rps against these
    endpoints. This throttles every call made through the client so
    the limit holds even if the agent fires several tools concurrently.
    """

    def __init__(self, rate: float) -> None:
        self._min_interval = 1.0 / rate
        self._lock = asyncio.Lock()
        self._last_call = 0.0

    async def wait(self) -> None:
        async with self._lock:
            now = time.monotonic()
            delay = self._last_call + self._min_interval - now
            if delay > 0:
                await asyncio.sleep(delay)
            self._last_call = time.monotonic()


class CdekShoppingApiError(RuntimeError):
    """Raised when the cdek.shopping API returns an error response."""

    def __init__(self, status_code: int, payload: Any) -> None:
        self.status_code = status_code
        self.payload = payload
        super().__init__(f"cdek.shopping API error {status_code}: {payload!r}")


class CdekShoppingClient:
    """Thin async wrapper around the cdek.shopping front-controller API.

    Auth is optional: most endpoints are public. Set CDEK_SHOPPING_TOKEN to
    enable the handful of endpoints that require a bearer token (e.g. orders).

    Requests are throttled to at most `max_rps` per second (default 5, the
    limit cdek.shopping asked agents to respect) regardless of how many
    tools the agent calls concurrently.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        language: str | None = None,
        timeout: float = 20.0,
        max_rps: float | None = None,
    ) -> None:
        self.base_url = base_url or os.environ.get("CDEK_SHOPPING_BASE_URL", DEFAULT_BASE_URL)
        self.token = token or os.environ.get("CDEK_SHOPPING_TOKEN")
        self.language = language or os.environ.get("CDEK_SHOPPING_LANG", "ru")
        rate = max_rps or float(os.environ.get("CDEK_SHOPPING_MAX_RPS", DEFAULT_MAX_RPS))
        self._rate_limiter = RateLimiter(rate)
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    @property
    def is_authenticated(self) -> bool:
        return bool(self.token)

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        require_auth: bool = False,
    ) -> Any:
        if require_auth and not self.token:
            raise CdekShoppingApiError(
                401,
                "This endpoint requires authentication. Set the CDEK_SHOPPING_TOKEN "
                "environment variable to a valid bearer token.",
            )

        headers = {"Accept-Language": self.language, "X-App-Name": APP_NAME}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        clean_params = _drop_none(params or {})

        await self._rate_limiter.wait()
        response = await self._client.request(
            method,
            path,
            params=clean_params,
            json=json_body,
            headers=headers,
        )

        try:
            payload = response.json()
        except ValueError:
            payload = response.text

        if response.is_error:
            raise CdekShoppingApiError(response.status_code, payload)

        return payload


def _drop_none(params: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in params.items() if v is not None}
