"""DataOps Control Plane API."""

import os

from fastapi import FastAPI, Response

from src.control_plane.adapters.adstream import (
    AdStreamAdapter,
)
from src.control_plane.adapters.kenya_economic import (
    KenyaEconomicAdapter,
)
from src.control_plane.metrics import (
    render_metrics,
)


def create_app(
    adapters=None,
) -> FastAPI:
    app = FastAPI(
        title="DataOps Control Plane",
        version="0.1.0",
    )

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

    def collect():
        return [
            adapter.collect()
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

    return app
