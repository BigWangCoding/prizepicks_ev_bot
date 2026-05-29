"""
prizepicks_ev_bot/ingestion/base_client.py

Base HTTP client that every API client inherits from.
Handles retries, timeouts, logging, and error handling in one place
so PrizePicksClient and OddsApiClient don't repeat this logic.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Final, cast

import httpx

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────

# HTTP status codes that are worth retrying (temporary server issues)
RETRYABLE_STATUS_CODES: Final[set[int]] = {429, 500, 502, 503, 504}

# HTTP status codes that mean retrying is pointless
NON_RETRYABLE_STATUS_CODES: Final[set[int]] = {401, 403, 404}

# Default headers sent with every request
DEFAULT_HEADERS: Final[dict[str, Any]] = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


# ─────────────────────────────────────────────────────────────────
# BASE CLIENT
# ─────────────────────────────────────────────────────────────────


class BaseClient:
    """
    Base class for all API clients in this project.

    Provides:
      - Async GET requests via httpx
      - Automatic retry with exponential backoff
      - Consistent logging across all clients
      - Timeout handling

    Subclasses should set self.base_url in their __init__
    and call super().__init__() to get this behavior.

    Example subclass usage:
        class MyClient(BaseClient):
            def __init__(self):
                super().__init__(base_url="https://api.example.com")

            async def get_data(self) -> list[dict]:
                return await self.get("/endpoint", params={"key": "value"})
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        """
        Args:
            base_url:        Root URL of the API, e.g. "https://api.prizepicks.com"
            timeout_seconds: How long to wait for a response before giving up.
            max_retries:     How many times to retry a failed request.
            extra_headers:   Any headers specific to this API (added on top of defaults).
        """
        self.base_url = base_url.rstrip("/")  # remove trailing slash if present
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

        # Merge default headers with any API-specific headers
        self.headers = {**DEFAULT_HEADERS, **(extra_headers or {})}

    # ─────────────────────────────────────────────────────────────
    # PUBLIC METHOD — this is what subclasses call
    # ─────────────────────────────────────────────────────────────

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        """
        Make an async GET request to base_url + path.

        Automatically retries on temporary failures with exponential backoff.
        Returns the parsed JSON body as a Python dict or list.

        Args:
            path:   URL path to append to base_url. E.g. "/projections"
            params: Optional query parameters. E.g. {"league_id": 7}
                    These become ?league_id=7 in the URL.

        Returns:
            Parsed JSON response body (dict or list).

        Raises:
            httpx.HTTPStatusError: If the request fails after all retries.
            httpx.RequestError:    If a network error occurs after all retries.
        """
        url = f"{self.base_url}{path}"

        for attempt in range(self.max_retries):
            try:
                response = await self._make_request(url, params)

                return response

            except httpx.HTTPStatusError as exc:
                status = exc.response.status_code

                # These errors won't be fixed by retrying — fail immediately
                if status in NON_RETRYABLE_STATUS_CODES:
                    logger.error(
                        "Non-retryable HTTP error %s for %s — check your API key or URL.",
                        status,
                        url,
                    )
                    raise

                # These are temporary — worth retrying
                if status in RETRYABLE_STATUS_CODES:
                    wait = self._backoff_seconds(attempt)
                    logger.warning(
                        "HTTP %s from %s (attempt %d/%d). Retrying in %.1fs.",
                        status,
                        url,
                        attempt + 1,
                        self.max_retries,
                        wait,
                    )
                    await asyncio.sleep(wait)
                    continue

                # Any other status code — fail immediately
                logger.error("Unexpected HTTP %s from %s.", status, url)
                raise

            except httpx.TimeoutException:
                wait = self._backoff_seconds(attempt)
                logger.warning(
                    "Request to %s timed out (attempt %d/%d). Retrying in %.1fs.",
                    url,
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

            except httpx.RequestError as exc:
                # Network-level error (DNS failure, connection refused, etc.)
                wait = self._backoff_seconds(attempt)
                logger.warning(
                    "Network error reaching %s: %s (attempt %d/%d). Retrying in %.1fs.",
                    url,
                    exc,
                    attempt + 1,
                    self.max_retries,
                    wait,
                )
                await asyncio.sleep(wait)
                continue

        # If we get here, all retries were exhausted
        logger.error(
            "All %d retries exhausted for %s. Giving up.",
            self.max_retries,
            url,
        )
        raise httpx.RequestError(f"All retries exhausted for {url}")

    # ─────────────────────────────────────────────────────────────
    # PRIVATE METHODS — internal implementation details
    # ─────────────────────────────────────────────────────────────

    async def _make_request(
        self,
        url: str,
        params: dict[str, Any] | None,
    ) -> dict[str, Any] | list[Any]:
        """
        Make a single GET request and return the parsed JSON.
        Opens and closes an httpx.AsyncClient for each call.

        The 'async with' block ensures the connection is always
        properly closed, even if an exception occurs.
        """
        async with httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout_seconds,
            follow_redirects=True,
        ) as client:
            logger.debug("GET %s | params=%s", url, params)

            response = await client.get(url, params=params)
            # print(response.headers) see how many credits are left
            # Log the result
            logger.debug(
                "Response %s from %s | %.0fms",
                response.status_code,
                url,
                response.elapsed.total_seconds() * 1000,
            )

            # Raise an exception if status code indicates an error (4xx or 5xx)
            response.raise_for_status()

            return cast(dict[str, Any] | list[Any], response.json())

    @staticmethod
    def _backoff_seconds(attempt: int) -> float:
        """
        Calculate how many seconds to wait before the next retry.

        Uses exponential backoff:
          attempt 0 → wait 1.0 second
          attempt 1 → wait 2.0 seconds
          attempt 2 → wait 4.0 seconds

        The max is capped at 30 seconds so we never wait too long.

        Args:
            attempt: Zero-based attempt number (0 = first failure).

        Returns:
            Number of seconds to wait.
        """
        return cast(float, min(2**attempt, 30.0))
