from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


class _JsonMixin:
    """Mixin for clean JSON output from dataclasses."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a plain dict (removes None values)."""
        return _strip_none(asdict(self))  # type: ignore[arg-type]

    def to_json(self, indent: int = 2) -> str:
        """Serialize to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def __repr__(self) -> str:
        return self.to_json()

    def __str__(self) -> str:
        return self.to_json()

    def __getitem__(self, key: str) -> Any:
        """Allow dict-style access: result['title']."""
        return getattr(self, key)


def _strip_none(d: Any) -> Any:
    if isinstance(d, dict):
        return {k: _strip_none(v) for k, v in d.items() if v is not None}
    if isinstance(d, list):
        return [_strip_none(i) for i in d]
    return d


@dataclass(frozen=True)
class SearchFilters(_JsonMixin):
    speaker: Optional[str] = None
    published_after: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    source: Optional[str] = None


@dataclass(frozen=True)
class SearchRequest(_JsonMixin):
    query: str
    max_results: int = 10
    ranking_mode: str = "embedding"
    include_answer: bool = False
    filters: Optional[SearchFilters] = None


@dataclass(frozen=True)
class SearchResult(_JsonMixin):
    id: str
    score: float
    url: str
    title: str
    snippet: str
    duration: int
    source: str
    rerank_score: Optional[float] = None
    transcript: Optional[str] = None
    thumbnail_url: Optional[str] = None
    keyframe_url: Optional[str] = None
    speaker: Optional[str] = None
    timestamp_start: Optional[float] = None
    timestamp_end: Optional[float] = None


@dataclass(frozen=True)
class SearchResponse(_JsonMixin):
    results: List[SearchResult]
    credits_used: int
    credits_remaining: int
    request_id: str
    answer: Optional[str] = None

    def __iter__(self):
        return iter(self.results)

    def __len__(self) -> int:
        return len(self.results)

    def __getitem__(self, index):
        if isinstance(index, int):
            return self.results[index]
        return getattr(self, index)


@dataclass(frozen=True)
class CreditBreakdown(_JsonMixin):
    included_remaining: int
    bonus_remaining: int
    paid_remaining: int


@dataclass(frozen=True)
class ExpiringCredit(_JsonMixin):
    grant_type: str
    credits: int
    expires_at: str


@dataclass(frozen=True)
class UsageResponse(_JsonMixin):
    tier: str
    plan_code: str
    period_start: str
    period_end: str
    credits_limit: int
    credits_used: int
    credits_remaining: int
    wallet_balance: int
    credit_breakdown: CreditBreakdown
    expiring_credits: List[ExpiringCredit]
    rate_limit_per_sec: int
    api_keys_active: int
    billing_hold: bool
    daily_free_remaining: int
    daily_free_limit: int
