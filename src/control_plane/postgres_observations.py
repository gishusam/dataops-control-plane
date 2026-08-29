"""Managed Postgres persistence for DataOps observations."""

from datetime import (
    datetime,
    timezone,
)

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

from src.control_plane.models import (
    PlatformHealth,
)


def utc_now() -> datetime:
    return datetime.now(
        timezone.utc
    )


class PostgresObservationStore:
    """Persistent last-known platform state and incident history."""

    def __init__(
        self,
        database_url: str,
    ):
        self.database_url = database_url
        self._initialize()

    def _connect(self):
        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    def _initialize(self) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS
                    dataops_platform_observations (
                        platform TEXT PRIMARY KEY,
                        telemetry_state TEXT NOT NULL,
                        status TEXT NOT NULL,
                        observed_at TIMESTAMPTZ,
                        payload JSONB NOT NULL,
                        updated_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS
                    dataops_incident_events (
                        id BIGSERIAL PRIMARY KEY,
                        platform TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        message TEXT NOT NULL,
                        occurred_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )

    def get_latest(
        self,
        platform: str,
    ) -> PlatformHealth | None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT payload
                    FROM dataops_platform_observations
                    WHERE platform = %s
                    """,
                    (platform,),
                )

                row = cursor.fetchone()

        if row is None:
            return None

        return PlatformHealth.model_validate(
            row["payload"]
        )

    def save(
        self,
        health: PlatformHealth,
    ) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO
                    dataops_platform_observations (
                        platform,
                        telemetry_state,
                        status,
                        observed_at,
                        payload,
                        updated_at
                    )
                    VALUES (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (platform)
                    DO UPDATE SET
                        telemetry_state =
                            EXCLUDED.telemetry_state,
                        status =
                            EXCLUDED.status,
                        observed_at =
                            EXCLUDED.observed_at,
                        payload =
                            EXCLUDED.payload,
                        updated_at =
                            EXCLUDED.updated_at
                    """,
                    (
                        health.platform,
                        health.telemetry_state,
                        health.status,
                        health.observed_at,
                        Jsonb(
                            health.model_dump(
                                mode="json"
                            )
                        ),
                        utc_now(),
                    ),
                )

    def record_incident(
        self,
        platform: str,
        event_type: str,
        message: str,
    ) -> None:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO
                    dataops_incident_events (
                        platform,
                        event_type,
                        message,
                        occurred_at
                    )
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        platform,
                        event_type,
                        message,
                        utc_now(),
                    ),
                )

    def recent_incidents(
        self,
        limit: int = 20,
    ) -> list[dict]:
        with self._connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        platform,
                        event_type,
                        message,
                        occurred_at
                    FROM dataops_incident_events
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
                )

                rows = cursor.fetchall()

        return [
            {
                "platform": row["platform"],
                "event_type": row[
                    "event_type"
                ],
                "message": row["message"],
                "occurred_at": (
                    row["occurred_at"]
                    .isoformat()
                ),
            }
            for row in rows
        ]
