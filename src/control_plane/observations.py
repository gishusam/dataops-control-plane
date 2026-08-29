"""Persistent platform observations and incident transitions."""

import json
import sqlite3
from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from src.control_plane.models import (
    PlatformHealth,
)


DEFAULT_DB_PATH = (
    Path("data")
    / "control-plane.db"
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


class ObservationStore:
    def __init__(
        self,
        path: str | Path = DEFAULT_DB_PATH,
    ):
        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize()

    def _connect(self):
        return sqlite3.connect(
            self.path
        )

    def _initialize(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS observations (
                    platform TEXT PRIMARY KEY,
                    telemetry_state TEXT NOT NULL,
                    status TEXT NOT NULL,
                    observed_at TEXT,
                    payload TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    occurred_at TEXT NOT NULL
                )
                """
            )

    def get_latest(
        self,
        platform: str,
    ) -> PlatformHealth | None:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT payload
                FROM observations
                WHERE platform = ?
                """,
                (platform,),
            ).fetchone()

        if row is None:
            return None

        return PlatformHealth.model_validate_json(
            row[0]
        )

    def save(
        self,
        health: PlatformHealth,
    ):
        payload = health.model_dump_json()
        now = utc_now()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO observations (
                    platform,
                    telemetry_state,
                    status,
                    observed_at,
                    payload,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(platform)
                DO UPDATE SET
                    telemetry_state = excluded.telemetry_state,
                    status = excluded.status,
                    observed_at = excluded.observed_at,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (
                    health.platform,
                    health.telemetry_state,
                    health.status,
                    health.observed_at,
                    payload,
                    now,
                ),
            )

    def record_incident(
        self,
        platform: str,
        event_type: str,
        message: str,
    ):
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO incidents (
                    platform,
                    event_type,
                    message,
                    occurred_at
                )
                VALUES (?, ?, ?, ?)
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
            rows = connection.execute(
                """
                SELECT
                    platform,
                    event_type,
                    message,
                    occurred_at
                FROM incidents
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "platform": row[0],
                "event_type": row[1],
                "message": row[2],
                "occurred_at": row[3],
            }
            for row in rows
        ]
