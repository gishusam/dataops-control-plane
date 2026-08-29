from datetime import (
    datetime,
    timezone,
)

from src.control_plane.adapters.kenya_economic import (
    KenyaEconomicAdapter,
)


class FakeJob:
    def __init__(
        self,
        rows,
    ):
        self.rows = rows

    def result(self):
        return self.rows


class FakeClient:
    def query(self, sql):
        if "pipeline_status" in sql:
            return FakeJob([
                {
                    "run_id": "run-001",
                    "started_at": datetime(
                        2026,
                        8,
                        28,
                        6,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    "completed_at": datetime(
                        2026,
                        8,
                        28,
                        6,
                        0,
                        42,
                        tzinfo=timezone.utc,
                    ),
                    "status": "success",
                    "sources_succeeded": 3,
                    "sources_failed": 0,
                    "rows_inserted": 27,
                    "dbt_status": "success",
                    "git_sha": "abc123",
                    "error_message": None,
                }
            ])

        if "source_health" in sql:
            return FakeJob([
                {
                    "source": "CBK",
                    "age_days": 1,
                    "expected_max_age_days": 4,
                    "freshness_status": "CURRENT",
                    "last_checked_at": datetime(
                        2026,
                        8,
                        28,
                        6,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    "last_error": None,
                },
                {
                    "source": "KNBS",
                    "age_days": 10,
                    "expected_max_age_days": 45,
                    "freshness_status": "CURRENT",
                    "last_checked_at": datetime(
                        2026,
                        8,
                        28,
                        6,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    "last_error": None,
                },
                {
                    "source": "WORLD_BANK",
                    "age_days": 80,
                    "expected_max_age_days": 400,
                    "freshness_status": "CURRENT",
                    "last_checked_at": datetime(
                        2026,
                        8,
                        28,
                        6,
                        0,
                        tzinfo=timezone.utc,
                    ),
                    "last_error": None,
                },
            ])

        raise AssertionError(sql)


class FailingClient:
    def query(self, sql):
        raise RuntimeError(
            "BigQuery unavailable"
        )


def test_kenya_economic_adapter_normalizes_bigquery_health():
    adapter = KenyaEconomicAdapter(
        project_id="kenya-econ-test",
        client=FakeClient(),
    )

    health = adapter.collect()

    assert health.platform == "kenya-economic"
    assert health.environment == "prod"
    assert health.status == "healthy"

    assert health.pipeline.name == "economic-refresh"
    assert health.pipeline.status == "success"
    assert health.pipeline.duration_seconds == 42.0

    assert len(health.sources) == 3
    assert health.sources[0].source == "CBK"
    assert health.sources[0].status == "current"

    assert health.quality_checks_passed == 1
    assert health.quality_checks_failed == 0
    assert health.incidents_open == 0


def test_kenya_economic_adapter_reports_unavailable():
    adapter = KenyaEconomicAdapter(
        project_id="kenya-econ-test",
        client=FailingClient(),
    )

    health = adapter.collect()

    assert health.status == "unavailable"
    assert health.pipeline.status == "unknown"
    assert health.incidents_open == 1
