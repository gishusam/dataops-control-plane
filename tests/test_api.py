from fastapi.testclient import TestClient

from src.control_plane.api import create_app
from src.control_plane.models import (
    PlatformHealth,
    PipelineHealth,
)


class FakeAdapter:
    def collect(self):
        return PlatformHealth(
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


def build_client():
    app = create_app(
        adapters=[FakeAdapter()]
    )
    return TestClient(app)


def test_health_endpoint():
    client = build_client()

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok"
    }


def test_platforms_endpoint_returns_normalized_health():
    client = build_client()

    response = client.get("/api/v1/platforms")

    assert response.status_code == 200

    body = response.json()

    assert len(body) == 1
    assert body[0]["platform"] == "adstream"
    assert body[0]["status"] == "healthy"


def test_metrics_endpoint_exposes_prometheus_metrics():
    client = build_client()

    response = client.get("/metrics")

    assert response.status_code == 200

    text = response.text

    assert "dataops_platform_up" in text
    assert "dataops_pipeline_duration_seconds" in text
    assert 'platform="adstream"' in text
