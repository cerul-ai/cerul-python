from __future__ import annotations

import asyncio
import os
import time
from collections.abc import Mapping
from email.utils import parsedate_to_datetime
from typing import Any, Dict, Optional, Union

import httpx

from ._version import __version__
from .errors import CerulError
from .types import (
    CreditBreakdown,
    ExpiringCredit,
    SearchFilters,
    SearchRequest,
    SearchResponse,
    SearchResult,
    UsageResponse,
)

DEFAULT_BASE_URL = "https://api.cerul.ai"
DEFAULT_TIMEOUT = 30.0
MAX_RETRY_ATTEMPTS = 3


def _normalize_base_url(base_url: Optional[str]) -> str:
    return (base_url or DEFAULT_BASE_URL).rstrip("/")


def _resolve_api_key(api_key: Optional[str]) -> str:
    resolved = api_key or os.getenv("CERUL_API_KEY")
    if not resolved:
        raise CerulError(0, "missing_api_key", "Cerul API key is required. Pass api_key or set CERUL_API_KEY.")
    return resolved


def _validate_search_request(request: SearchRequest) -> None:
    if not isinstance(request.query, str) or not request.query.strip():
        raise ValueError("query must be a non-empty string")
    if len(request.query) > 400:
        raise ValueError("query must be 400 characters or fewer")
    if request.max_results < 1 or request.max_results > 50:
        raise ValueError("max_results must be between 1 and 50")
    if request.ranking_mode not in {"embedding", "rerank"}:
        raise ValueError("ranking_mode must be 'embedding' or 'rerank'")
    if request.filters and request.filters.published_after:
        value = request.filters.published_after
        if len(value) != 10 or value[4] != "-" or value[7] != "-":
            raise ValueError("filters.published_after must be in YYYY-MM-DD format")


def _coerce_filters(filters: Optional[Union[Mapping[str, Any], SearchFilters]]) -> Optional[SearchFilters]:
    if filters is None:
        return None
    if isinstance(filters, SearchFilters):
        return filters
    return SearchFilters(
        speaker=str(filters["speaker"]) if filters.get("speaker") is not None else None,
        published_after=str(filters["published_after"]) if filters.get("published_after") is not None else None,
        min_duration=int(filters["min_duration"]) if filters.get("min_duration") is not None else None,
        max_duration=int(filters["max_duration"]) if filters.get("max_duration") is not None else None,
        source=str(filters["source"]) if filters.get("source") is not None else None,
    )


def _parse_request_id(response: httpx.Response, payload: Any) -> Optional[str]:
    header_request_id = response.headers.get("x-request-id") or response.headers.get("request-id")
    if header_request_id:
        return header_request_id
    if isinstance(payload, dict) and isinstance(payload.get("request_id"), str):
        return str(payload["request_id"])
    return None


def _parse_error_response(response: httpx.Response) -> CerulError:
    payload: Any = None
    try:
        payload = response.json()
    except ValueError:
        payload = None

    error_payload = payload.get("error") if isinstance(payload, dict) else None
    code = "api_error" if response.status_code >= 500 else "invalid_request"
    if response.status_code == 401:
        code = "unauthorized"
    elif response.status_code == 403:
        code = "forbidden"
    elif response.status_code == 404:
        code = "not_found"
    elif response.status_code == 429:
        code = "rate_limited"
    elif isinstance(error_payload, dict) and isinstance(error_payload.get("code"), str):
        code = str(error_payload["code"])

    message = f"Cerul API request failed with status {response.status_code}"
    if isinstance(error_payload, dict) and isinstance(error_payload.get("message"), str):
        message = str(error_payload["message"])

    return CerulError(response.status_code, code, message, _parse_request_id(response, payload))


def _retry_after_seconds(response: httpx.Response, attempt: int) -> float:
    retry_after = response.headers.get("retry-after")
    if retry_after:
        try:
            value = float(retry_after)
            if value >= 0:
                return value
        except ValueError:
            try:
                dt = parsedate_to_datetime(retry_after)
                return max(dt.timestamp() - time.time(), 0.0)
            except (TypeError, ValueError, OverflowError):
                pass
    return 0.25 * (2 ** (attempt - 1))


def _should_retry(status_code: int, retry_enabled: bool) -> bool:
    return retry_enabled and (status_code == 429 or status_code >= 500)


def _user_agent() -> str:
    return f"cerul-python/{__version__}"


def _build_search_response(payload: Mapping[str, Any]) -> SearchResponse:
    results = [
        SearchResult(
            id=str(item["id"]),
            score=float(item["score"]),
            rerank_score=float(item["rerank_score"]) if item.get("rerank_score") is not None else None,
            url=str(item["url"]),
            title=str(item["title"]),
            snippet=str(item["snippet"]),
            transcript=str(item["transcript"]) if item.get("transcript") is not None else None,
            thumbnail_url=str(item["thumbnail_url"]) if item.get("thumbnail_url") is not None else None,
            keyframe_url=str(item["keyframe_url"]) if item.get("keyframe_url") is not None else None,
            duration=int(item["duration"]),
            source=str(item["source"]),
            speaker=str(item["speaker"]) if item.get("speaker") is not None else None,
            timestamp_start=float(item["timestamp_start"]) if item.get("timestamp_start") is not None else None,
            timestamp_end=float(item["timestamp_end"]) if item.get("timestamp_end") is not None else None,
        )
        for item in payload.get("results", [])
    ]
    return SearchResponse(
        results=results,
        answer=str(payload["answer"]) if payload.get("answer") is not None else None,
        credits_used=int(payload["credits_used"]),
        credits_remaining=int(payload["credits_remaining"]),
        request_id=str(payload["request_id"]),
    )


def _build_usage_response(payload: Mapping[str, Any]) -> UsageResponse:
    breakdown_payload = payload.get("credit_breakdown")
    expiring_payload = payload["expiring_credits"]
    if not isinstance(breakdown_payload, Mapping):
        raise KeyError("credit_breakdown")
    if not isinstance(expiring_payload, list):
        raise TypeError("expiring_credits must be a list")
    return UsageResponse(
        tier=str(payload["tier"]),
        plan_code=str(payload["plan_code"]),
        period_start=str(payload["period_start"]),
        period_end=str(payload["period_end"]),
        credits_limit=int(payload["credits_limit"]),
        credits_used=int(payload["credits_used"]),
        credits_remaining=int(payload["credits_remaining"]),
        wallet_balance=int(payload["wallet_balance"]),
        credit_breakdown=CreditBreakdown(
            included_remaining=int(breakdown_payload["included_remaining"]),
            bonus_remaining=int(breakdown_payload["bonus_remaining"]),
            paid_remaining=int(breakdown_payload["paid_remaining"]),
        ),
        expiring_credits=[
            ExpiringCredit(
                grant_type=str(item["grant_type"]),
                credits=int(item["credits"]),
                expires_at=str(item["expires_at"]),
            )
            for item in expiring_payload
        ],
        rate_limit_per_sec=int(payload["rate_limit_per_sec"]),
        api_keys_active=int(payload["api_keys_active"]),
        billing_hold=bool(payload["billing_hold"]),
        daily_free_remaining=int(payload["daily_free_remaining"]),
        daily_free_limit=int(payload["daily_free_limit"]),
    )


class Cerul:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry: bool = False,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be a positive number")
        self._retry = retry
        self._client = httpx.Client(
            base_url=_normalize_base_url(base_url),
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {_resolve_api_key(api_key)}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": _user_agent(),
                "X-Cerul-Client-Source": "sdk-python",
            },
            transport=transport,
        )

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "Cerul":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def _request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                response = self._client.request(method, path, json=json)
            except httpx.TimeoutException as error:
                raise CerulError(0, "timeout", "The request timed out.") from error
            except httpx.HTTPError as error:
                raise CerulError(0, "network_error", str(error)) from error

            if response.is_success:
                return response.json()

            error = _parse_error_response(response)
            if attempt < MAX_RETRY_ATTEMPTS and _should_retry(response.status_code, self._retry):
                time.sleep(_retry_after_seconds(response, attempt))
                continue
            raise error

        raise CerulError(0, "api_error", "Request failed after exhausting retries.")

    def search(
        self,
        query: str,
        max_results: int = 10,
        ranking_mode: str = "embedding",
        include_answer: bool = False,
        filters: Optional[Union[Mapping[str, Any], SearchFilters]] = None,
    ) -> SearchResponse:
        request = SearchRequest(
            query=query,
            max_results=max_results,
            ranking_mode=ranking_mode,
            include_answer=include_answer,
            filters=_coerce_filters(filters),
        )
        _validate_search_request(request)
        payload = self._request("POST", "/v1/search", json=request.to_dict())
        return _build_search_response(payload)

    def usage(self) -> UsageResponse:
        payload = self._request("GET", "/v1/usage")
        return _build_usage_response(payload)


class AsyncCerul:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        retry: bool = False,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        if timeout <= 0:
            raise ValueError("timeout must be a positive number")
        self._retry = retry
        self._client = httpx.AsyncClient(
            base_url=_normalize_base_url(base_url),
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {_resolve_api_key(api_key)}",
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": _user_agent(),
                "X-Cerul-Client-Source": "sdk-python",
            },
            transport=transport,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncCerul":
        return self

    async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        await self.close()

    async def _request(self, method: str, path: str, json: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                response = await self._client.request(method, path, json=json)
            except httpx.TimeoutException as error:
                raise CerulError(0, "timeout", "The request timed out.") from error
            except httpx.HTTPError as error:
                raise CerulError(0, "network_error", str(error)) from error

            if response.is_success:
                return response.json()

            error = _parse_error_response(response)
            if attempt < MAX_RETRY_ATTEMPTS and _should_retry(response.status_code, self._retry):
                await asyncio.sleep(_retry_after_seconds(response, attempt))
                continue
            raise error

        raise CerulError(0, "api_error", "Request failed after exhausting retries.")

    async def search(
        self,
        query: str,
        max_results: int = 10,
        ranking_mode: str = "embedding",
        include_answer: bool = False,
        filters: Optional[Union[Mapping[str, Any], SearchFilters]] = None,
    ) -> SearchResponse:
        request = SearchRequest(
            query=query,
            max_results=max_results,
            ranking_mode=ranking_mode,
            include_answer=include_answer,
            filters=_coerce_filters(filters),
        )
        _validate_search_request(request)
        payload = await self._request("POST", "/v1/search", json=request.to_dict())
        return _build_search_response(payload)

    async def usage(self) -> UsageResponse:
        payload = await self._request("GET", "/v1/usage")
        return _build_usage_response(payload)
