"""Normalized operational models for managed data platforms."""

from typing import Literal

from pydantic import BaseModel


PlatformStatus = Literal[
    "healthy",
    "degraded",
    "unavailable",
]

PipelineStatus = Literal[
    "success",
    "degraded",
    "failed",
    "unknown",
]

FreshnessStatus = Literal[
    "current",
    "stale",
    "degraded",
    "unknown",
]


class PipelineHealth(BaseModel):
    name: str
    status: PipelineStatus
    duration_seconds: float | None = None
    last_success_at: str | None = None


class SourceFreshness(BaseModel):
    source: str
    status: FreshnessStatus
    age_days: int | None = None
    threshold_days: int | None = None
    last_checked_at: str | None = None
    last_error: str | None = None


class PlatformHealth(BaseModel):
    platform: str
    environment: str = "demo"
    status: PlatformStatus
    pipeline: PipelineHealth

    # Generic scalar retained for platforms that naturally expose one
    # freshness value.
    freshness_seconds: float | None = None

    # Source-aware freshness for batch platforms such as Kenya Economic.
    sources: list[SourceFreshness] = []

    quality_checks_passed: int = 0
    quality_checks_failed: int = 0

    incidents_open: int = 0

    stream_throughput: float | None = None
    kafka_consumer_lag: int | None = None
    quarantine_records: int | None = None
