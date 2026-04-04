from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional


@dataclass(frozen=True)
class SearchFilters:
    speaker: Optional[str] = None
    published_after: Optional[str] = None
    min_duration: Optional[int] = None
    max_duration: Optional[int] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            key: value
            for key, value in {
                "speaker": self.speaker,
                "published_after": self.published_after,
                "min_duration": self.min_duration,
                "max_duration": self.max_duration,
                "source": self.source,
            }.items()
            if value is not None
        }


@dataclass(frozen=True)
class SearchRequest:
    query: str
    max_results: int = 10
    ranking_mode: str = "embedding"
    include_answer: bool = False
    filters: Optional[SearchFilters] = None

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "query": self.query,
            "max_results": self.max_results,
            "ranking_mode": self.ranking_mode,
            "include_answer": self.include_answer,
        }
        if self.filters is not None:
            payload["filters"] = self.filters.to_dict()
        return payload


@dataclass(frozen=True)
class SearchResult:
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
class SearchResponse:
    results: List[SearchResult]
    credits_used: int
    credits_remaining: int
    request_id: str
    answer: Optional[str] = None


@dataclass(frozen=True)
class CreditBreakdown:
    included_remaining: int
    bonus_remaining: int
    paid_remaining: int


@dataclass(frozen=True)
class ExpiringCredit:
    grant_type: str
    credits: int
    expires_at: str


@dataclass(frozen=True)
class UsageResponse:
    tier: str
    period_start: str
    period_end: str
    credits_limit: int
    credits_used: int
    credits_remaining: int
    rate_limit_per_sec: int
    api_keys_active: int
    plan_code: Optional[str] = None
    wallet_balance: Optional[int] = None
    credit_breakdown: Optional[CreditBreakdown] = None
    expiring_credits: List[ExpiringCredit] = field(default_factory=list)
    billing_hold: Optional[bool] = None
    daily_free_remaining: Optional[int] = None
    daily_free_limit: Optional[int] = None


FiltersInput = Optional[Mapping[str, Any]]
