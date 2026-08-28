"""Prometheus metric generation for normalized platform health."""

from prometheus_client import (
    CollectorRegistry,
    Gauge,
    generate_latest,
)

from src.control_plane.models import (
    PlatformHealth,
)


def render_metrics(
    platforms: list[PlatformHealth],
) -> bytes:
    registry = CollectorRegistry()

    platform_up = Gauge(
        "dataops_platform_up",
        "Whether the managed platform is healthy.",
        ["platform", "environment"],
        registry=registry,
    )

    pipeline_duration = Gauge(
        "dataops_pipeline_duration_seconds",
        "Latest observed pipeline duration.",
        [
            "platform",
            "pipeline",
            "environment",
        ],
        registry=registry,
    )

    quality_passed = Gauge(
        "dataops_quality_checks_passed",
        "Number of passing quality checks.",
        ["platform", "environment"],
        registry=registry,
    )

    quality_failed = Gauge(
        "dataops_quality_checks_failed",
        "Number of failing quality checks.",
        ["platform", "environment"],
        registry=registry,
    )

    incidents_open = Gauge(
        "dataops_incidents_open",
        "Number of currently open incidents.",
        ["platform", "environment"],
        registry=registry,
    )

    source_freshness = Gauge(
        "dataops_source_freshness_days",
        "Age of the latest source observation.",
        [
            "platform",
            "source",
            "environment",
        ],
        registry=registry,
    )

    source_freshness_limit = Gauge(
        "dataops_source_freshness_limit_days",
        "Maximum expected source age.",
        [
            "platform",
            "source",
            "environment",
        ],
        registry=registry,
    )

    source_current = Gauge(
        "dataops_source_current",
        "Whether a source is currently within its freshness contract.",
        [
            "platform",
            "source",
            "environment",
        ],
        registry=registry,
    )

    for platform in platforms:
        labels = {
            "platform": platform.platform,
            "environment": platform.environment,
        }

        platform_up.labels(
            **labels
        ).set(
            1
            if platform.status
            == "healthy"
            else 0
        )

        if (
            platform.pipeline
            .duration_seconds
            is not None
        ):
            pipeline_duration.labels(
                platform=platform.platform,
                pipeline=(
                    platform.pipeline.name
                ),
                environment=(
                    platform.environment
                ),
            ).set(
                platform.pipeline
                .duration_seconds
            )

        quality_passed.labels(
            **labels
        ).set(
            platform
            .quality_checks_passed
        )

        quality_failed.labels(
            **labels
        ).set(
            platform
            .quality_checks_failed
        )

        incidents_open.labels(
            **labels
        ).set(
            platform.incidents_open
        )

        for source in platform.sources:
            source_labels = {
                "platform": (
                    platform.platform
                ),
                "source": source.source,
                "environment": (
                    platform.environment
                ),
            }

            if source.age_days is not None:
                source_freshness.labels(
                    **source_labels
                ).set(
                    source.age_days
                )

            if (
                source.threshold_days
                is not None
            ):
                source_freshness_limit.labels(
                    **source_labels
                ).set(
                    source.threshold_days
                )

            source_current.labels(
                **source_labels
            ).set(
                1
                if source.status
                == "current"
                else 0
            )

    return generate_latest(
        registry
    )
