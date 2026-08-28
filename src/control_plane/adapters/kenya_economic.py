"""Kenya Economic Platform operational telemetry adapter."""

from datetime import datetime

from google.cloud import bigquery

from src.control_plane.adapters.base import (
    PlatformAdapter,
)
from src.control_plane.models import (
    PipelineHealth,
    PlatformHealth,
    SourceFreshness,
)


class KenyaEconomicAdapter(PlatformAdapter):
    def __init__(
        self,
        project_id: str,
        client=None,
    ):
        self.project_id = project_id

        self.client = (
            client
            or bigquery.Client(
                project=project_id
            )
        )

    @staticmethod
    def _iso(value):
        if value is None:
            return None

        if isinstance(value, datetime):
            return value.isoformat()

        return str(value)

    @staticmethod
    def _value(row, key, default=None):
        if isinstance(row, dict):
            return row.get(key, default)

        try:
            return row[key]
        except (KeyError, TypeError):
            return getattr(
                row,
                key,
                default,
            )

    def unavailable(self) -> PlatformHealth:
        return PlatformHealth(
            platform="kenya-economic",
            environment="prod",
            status="unavailable",
            pipeline=PipelineHealth(
                name="economic-refresh",
                status="unknown",
            ),
        )

    def collect(self) -> PlatformHealth:
        try:
            pipeline_rows = list(
                self.client.query(
                    f"""
                    SELECT *
                    FROM `{self.project_id}.marts.pipeline_status`
                    """
                ).result()
            )

            source_rows = list(
                self.client.query(
                    f"""
                    SELECT *
                    FROM `{self.project_id}.marts.source_health`
                    ORDER BY source
                    """
                ).result()
            )

        except Exception:
            return self.unavailable()

        if not pipeline_rows:
            return self.unavailable()

        run = pipeline_rows[0]

        status = self._value(
            run,
            "status",
            "failed",
        )

        dbt_status = self._value(
            run,
            "dbt_status",
            "failed",
        )

        started_at = self._value(
            run,
            "started_at",
        )

        completed_at = self._value(
            run,
            "completed_at",
        )

        duration_seconds = None

        if (
            started_at is not None
            and completed_at is not None
        ):
            duration_seconds = (
                completed_at - started_at
            ).total_seconds()

        freshness = []

        for row in source_rows:
            raw_status = str(
                self._value(
                    row,
                    "freshness_status",
                    "UNKNOWN",
                )
            ).lower()

            normalized_status = {
                "current": "current",
                "stale": "stale",
                "degraded": "degraded",
            }.get(
                raw_status,
                "unknown",
            )

            freshness.append(
                SourceFreshness(
                    source=str(
                        self._value(
                            row,
                            "source",
                            "unknown",
                        )
                    ),
                    status=normalized_status,
                    age_days=self._value(
                        row,
                        "age_days",
                    ),
                    threshold_days=(
                        self._value(
                            row,
                            "expected_max_age_days",
                        )
                    ),
                    last_checked_at=self._iso(
                        self._value(
                            row,
                            "last_checked_at",
                        )
                    ),
                    last_error=self._value(
                        row,
                        "last_error",
                    ),
                )
            )

        any_source_unhealthy = any(
            item.status
            in {
                "stale",
                "degraded",
                "unknown",
            }
            for item in freshness
        )

        if status == "failed":
            platform_status = "degraded"

        elif (
            status == "degraded"
            or any_source_unhealthy
        ):
            platform_status = "degraded"

        else:
            platform_status = "healthy"

        quality_passed = (
            1
            if dbt_status == "success"
            else 0
        )

        quality_failed = (
            0
            if dbt_status == "success"
            else 1
        )

        return PlatformHealth(
            platform="kenya-economic",
            environment="prod",
            status=platform_status,
            pipeline=PipelineHealth(
                name="economic-refresh",
                status=status,
                duration_seconds=(
                    duration_seconds
                ),
                last_success_at=(
                    self._iso(
                        completed_at
                    )
                    if status == "success"
                    else None
                ),
            ),
            sources=freshness,
            quality_checks_passed=(
                quality_passed
            ),
            quality_checks_failed=(
                quality_failed
            ),
        )
