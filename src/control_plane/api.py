"""DataOps Control Plane API."""

import os
from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from fastapi import (
    FastAPI,
    Response,
)
from fastapi.responses import FileResponse

from src.control_plane.adapters.adstream import (
    AdStreamAdapter,
)
from src.control_plane.adapters.kenya_economic import (
    KenyaEconomicAdapter,
)
from src.control_plane.metrics import (
    render_metrics,
)
from src.control_plane.models import (
    PlatformHealth,
)
from src.control_plane.observations import (
    ObservationStore,
)
from src.control_plane.postgres_observations import (
    PostgresObservationStore,
)


def now_iso() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def create_app(
    adapters=None,
    observation_store=None,
) -> FastAPI:
    app = FastAPI(
        title="DataOps Control Plane",
        version="0.2.0",
    )

    if observation_store is not None:
        store = observation_store
    else:
        database_url = os.getenv(
            "DATAOPS_POSTGRES_URL"
        )

        if database_url:
            store = PostgresObservationStore(
                database_url
            )
        else:
            store = ObservationStore()

    platform_adapters = adapters

    if platform_adapters is None:
        platform_adapters = [
            AdStreamAdapter(
                base_url=os.getenv(
                    "ADSTREAM_URL",
                    "http://127.0.0.1:8010",
                )
            )
        ]

        project_id = os.getenv(
            "GCP_PROJECT_ID"
        )

        if project_id:
            platform_adapters.append(
                KenyaEconomicAdapter(
                    project_id=project_id
                )
            )

    def normalize_collection(
        adapter,
    ) -> PlatformHealth:
        current = adapter.collect()

        previous = store.get_latest(
            current.platform
        )

        if current.status != "unavailable":
            live = current.model_copy(
                update={
                    "telemetry_state": "live",
                    "observed_at": now_iso(),
                }
            )

            if (
                previous is not None
                and previous.telemetry_state
                == "stale"
            ):
                store.record_incident(
                    platform=live.platform,
                    event_type="recovered",
                    message=(
                        f"{live.platform} telemetry recovered"
                    ),
                )

            store.save(live)
            return live

        if previous is None:
            unknown = current.model_copy(
                update={
                    "telemetry_state": "unknown",
                    "observed_at": None,
                }
            )

            return unknown

        stale = previous.model_copy(
            update={
                "telemetry_state": "stale",
                "incidents_open": 1,
            }
        )

        if (
            previous.telemetry_state
            != "stale"
        ):
            store.record_incident(
                platform=stale.platform,
                event_type="telemetry_lost",
                message=(
                    f"{stale.platform} telemetry became stale"
                ),
            )

        store.save(stale)

        return stale

    def collect():
        return [
            normalize_collection(
                adapter
            )
            for adapter
            in platform_adapters
        ]

    @app.get("/health")
    def health():
        return {
            "status": "ok"
        }

    @app.get("/api/v1/platforms")
    def platforms():
        return collect()

    @app.get("/api/v1/incidents")
    def incidents():
        return store.recent_incidents()

    @app.get("/metrics")
    def metrics():
        return Response(
            content=render_metrics(
                collect()
            ),
            media_type=(
                "text/plain; "
                "version=0.0.4"
            ),
        )

    dashboard_path = Path(
        "dashboard/control-plane.html"
    )

    @app.get("/")
    def dashboard():
        if dashboard_path.exists():
            return FileResponse(
                dashboard_path
            )

        return {
            "service": (
                "DataOps Control Plane"
            )
        }

    return app
