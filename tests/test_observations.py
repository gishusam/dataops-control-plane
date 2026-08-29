from pathlib import Path

from src.control_plane.models import (
    PipelineHealth,
    PlatformHealth,
)
from src.control_plane.observations import (
    ObservationStore,
)


def test_observation_store_persists_latest_state(
    tmp_path: Path,
):
    store = ObservationStore(
        tmp_path / "test.db"
    )

    health = PlatformHealth(
        platform="adstream",
        environment="demo",
        status="healthy",
        telemetry_state="live",
        observed_at=(
            "2026-08-29T05:00:00+00:00"
        ),
        pipeline=PipelineHealth(
            name="medallion",
            status="success",
            duration_seconds=83.8,
        ),
    )

    store.save(health)

    loaded = store.get_latest(
        "adstream"
    )

    assert loaded is not None
    assert loaded.status == "healthy"
    assert loaded.telemetry_state == "live"


def test_incident_history_is_persisted(
    tmp_path: Path,
):
    store = ObservationStore(
        tmp_path / "test.db"
    )

    store.record_incident(
        platform="adstream",
        event_type="telemetry_lost",
        message="AdStream telemetry became stale",
    )

    incidents = (
        store.recent_incidents()
    )

    assert len(incidents) == 1
    assert (
        incidents[0]["platform"]
        == "adstream"
    )
    assert (
        incidents[0]["event_type"]
        == "telemetry_lost"
    )
