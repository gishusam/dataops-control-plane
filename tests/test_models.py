from src.control_plane.models import (
    PlatformHealth,
    PipelineHealth,
)


def test_platform_health_represents_normalized_state():
    health = PlatformHealth(
        platform="adstream",
        environment="demo",
        status="healthy",
        pipeline=PipelineHealth(
            name="medallion",
            status="success",
            duration_seconds=83.84,
        ),
        quality_checks_passed=4,
        quality_checks_failed=0,
    )

    assert health.platform == "adstream"
    assert health.status == "healthy"
    assert health.pipeline.status == "success"
    assert health.pipeline.duration_seconds == 83.84
    assert health.quality_checks_passed == 4
