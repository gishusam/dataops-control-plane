"""AdStream operational telemetry adapter."""

import httpx

from src.control_plane.adapters.base import (
    PlatformAdapter,
)
from src.control_plane.models import (
    PipelineHealth,
    PlatformHealth,
)


class AdStreamAdapter(PlatformAdapter):
    def __init__(
        self,
        base_url: str,
        client=None,
    ):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client()

    def unavailable(self) -> PlatformHealth:
        return PlatformHealth(
            platform="adstream",
            environment="demo",
            status="unavailable",
            pipeline=PipelineHealth(
                name="medallion",
                status="unknown",
                duration_seconds=None,
                last_success_at=None,
            ),
            quality_checks_passed=0,
            quality_checks_failed=0,
        )

    def collect(self) -> PlatformHealth:
        try:
            response = self.client.get(
                (
                    f"{self.base_url}"
                    "/api/v1/pipeline-health"
                ),
                timeout=15.0,
            )

            response.raise_for_status()

            data = response.json()

        except (
            httpx.HTTPError,
            ValueError,
        ):
            return self.unavailable()

        system = data.get(
            "system",
            {},
        )

        latest_run = data.get(
            "latest_run"
        )

        stages = data.get(
            "stages",
            [],
        )

        api_healthy = (
            system.get("api")
            == "healthy"
        )

        database_ready = (
            system.get(
                "serving_database"
            )
            == "ready"
        )

        pipeline_status = (
            latest_run.get(
                "status",
                "unknown",
            )
            if latest_run
            else "unknown"
        )

        platform_status = (
            "healthy"
            if (
                api_healthy
                and database_ready
                and pipeline_status
                == "success"
            )
            else "degraded"
        )

        passed = sum(
            1
            for stage in stages
            if stage.get("status")
            == "success"
        )

        failed = sum(
            1
            for stage in stages
            if stage.get("status")
            == "failed"
        )

        duration_seconds = None

        if latest_run:
            duration_ms = (
                latest_run.get(
                    "duration_ms"
                )
            )

            if duration_ms is not None:
                duration_seconds = (
                    float(duration_ms)
                    / 1000
                )

        return PlatformHealth(
            platform="adstream",
            environment="demo",
            status=platform_status,
            pipeline=PipelineHealth(
                name="medallion",
                status=pipeline_status,
                duration_seconds=(
                    duration_seconds
                ),
                last_success_at=(
                    latest_run.get(
                        "recorded_at"
                    )
                    if (
                        latest_run
                        and pipeline_status
                        == "success"
                    )
                    else None
                ),
            ),
            quality_checks_passed=passed,
            quality_checks_failed=failed,
        )
