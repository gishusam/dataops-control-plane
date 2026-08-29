import httpx

from src.control_plane.adapters.adstream import (
    AdStreamAdapter,
)


class FakeResponse:
    def raise_for_status(self):
        return None

    def json(self):
        return {
            "system": {
                "api": "healthy",
                "serving_database": "ready",
            },
            "latest_run": {
                "run_id": "manual__2026-08-28",
                "status": "success",
                "duration_ms": 83840,
                "recorded_at": (
                    "2026-08-28T10:28:23+00:00"
                ),
            },
            "stages": [
                {
                    "stage": "silver",
                    "status": "success",
                },
                {
                    "stage": "gold",
                    "status": "success",
                },
                {
                    "stage": "quality",
                    "status": "success",
                },
                {
                    "stage": "serving",
                    "status": "success",
                },
            ],
            "recent_runs": [],
        }


class FakeClient:
    def get(
        self,
        url,
        timeout,
    ):
        assert url.endswith(
            "/api/v1/pipeline-health"
        )
        assert timeout == 15.0
        return FakeResponse()


class FailingClient:
    def get(
        self,
        url,
        timeout,
    ):
        raise httpx.ConnectError(
            "connection refused"
        )


def test_adstream_adapter_normalizes_pipeline_health():
    adapter = AdStreamAdapter(
        base_url="http://adstream:8010",
        client=FakeClient(),
    )

    health = adapter.collect()

    assert health.platform == "adstream"
    assert health.status == "healthy"
    assert health.pipeline.name == "medallion"
    assert health.pipeline.status == "success"
    assert health.pipeline.duration_seconds == 83.84
    assert health.quality_checks_passed == 4
    assert health.quality_checks_failed == 0
    assert health.incidents_open == 0


def test_adstream_adapter_reports_unavailable_when_source_is_down():
    adapter = AdStreamAdapter(
        base_url="http://adstream:8010",
        client=FailingClient(),
    )

    health = adapter.collect()

    assert health.platform == "adstream"
    assert health.status == "unavailable"
    assert health.pipeline.status == "unknown"
    assert health.quality_checks_passed == 0
    assert health.quality_checks_failed == 0
    assert health.incidents_open == 1
