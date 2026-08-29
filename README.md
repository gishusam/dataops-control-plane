# DataOps Control Plane

> **A production DataOps control plane that monitors independently deployed data platforms through one operational model — health, pipeline state, freshness, quality, incidents, and recovery.**

**Python · FastAPI · Google Cloud Run · BigQuery · PostgreSQL · Docker · Terraform · GitHub Actions**

## The idea in 10 seconds

Two data platforms. Different architectures. Different telemetry. **One operational view.**

```text
                         DataOps Control Plane
                            Google Cloud Run
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
               AdStream API                Kenya Economic
                Cloud Run                     BigQuery
                    │
                    ▼
             Supabase Postgres

                         │
                         ▼
                Persistent DataOps State
                 observations + incidents
```

The control plane answers the questions that matter after a pipeline reaches production:

**Is it up? Did the pipeline succeed? Is the data fresh? Did quality pass? What failed? Has it recovered?**

## What this demonstrates

| Capability | Implementation |
|---|---|
| **Multi-platform operations** | Normalizes medallion/streaming and batch/warehouse platforms into one health model |
| **Failure isolation** | One platform can fail without taking down fleet monitoring |
| **Last-known-state** | Preserves operational context when live telemetry disappears |
| **Incident lifecycle** | Detects telemetry loss and recovery rather than exposing raw connection failures |
| **Freshness contracts** | Evaluates source age against platform-specific thresholds |
| **Production deployment** | Containerized services designed for Google Cloud Run |
| **Persistent state** | PostgreSQL/Supabase stores observations and incident history |
| **Cloud telemetry** | Kenya Economic operational state is read from BigQuery |
| **Observability** | Prometheus-compatible metrics plus a purpose-built operations dashboard |
| **Production engineering** | Docker, CI, Terraform, tests, SLOs, runbooks, backfill and disaster-recovery docs |

## Why this project exists

Data engineering projects often stop at:

```text
source → transform → warehouse → dashboard
```

Production ownership starts after that.

Teams still need to know whether platforms are reachable, whether the latest run succeeded, whether upstream data is late, whether quality gates passed, and what happened during an outage.

This project explores that layer: **operating multiple data platforms as a fleet rather than treating every pipeline as an isolated script.**

## Architecture

### AdStream

A medallion-style advertising data platform with its own hosted operational API. The control plane consumes API/database readiness, latest pipeline state, stage execution, duration, quality state, and recent runs.

AdStream is independently deployed to **Google Cloud Run** and persists serving and pipeline metrics in **Supabase PostgreSQL**.

### Kenya Economic

A batch economic-data platform backed by **Google BigQuery**. The control plane reads operational marts and evaluates both pipeline execution and source freshness.

| Source | Freshness budget |
|---|---:|
| CBK | 4 days |
| KNBS | 45 days |
| World Bank | 400 days |

A successful pipeline alone is therefore not enough to declare the platform healthy: its underlying data must also be current.

### DataOps Control Plane

FastAPI translates platform-specific telemetry into a common operational contract:

```text
PlatformHealth
├── platform / environment
├── status / telemetry_state / observed_at
├── pipeline
│   ├── status
│   ├── duration
│   └── last_success
├── sources[]
├── quality_checks
└── incidents
```

That model powers the API, dashboard, incident logic, and Prometheus metrics.

## Resilience: failure is a state, not an exception

```text
AdStream reachable
      │
      ▼
 HEALTHY · LIVE
      │ telemetry lost
      ▼
last known state preserved
incident opened
telemetry marked STALE
      │ platform recovers
      ▼
incident resolved
 HEALTHY · LIVE
```

The control plane distinguishes:

- **LIVE** — current telemetry is reachable.
- **STALE** — telemetry is unavailable, but a previous observation is retained.
- **UNKNOWN** — the platform has never been successfully observed.

A monitored system going offline therefore does not erase its operational history or crash fleet monitoring.

## Operations dashboard

The purpose-built control-plane dashboard surfaces:

- fleet health;
- live vs stale telemetry;
- pipeline state and duration;
- quality checks;
- open incidents;
- source freshness;
- incident and recovery history.

This is intentionally an **operations view**, not a business analytics dashboard.

## API

| Endpoint | Purpose |
|---|---|
| `GET /health` | Control-plane liveness |
| `GET /api/v1/platforms` | Normalized fleet health |
| `GET /api/v1/incidents` | Incident/recovery history |
| `GET /metrics` | Prometheus-compatible telemetry |

Representative metrics include:

```text
dataops_platform_up
dataops_telemetry_live
dataops_pipeline_duration_seconds
dataops_quality_checks_passed
dataops_quality_checks_failed
dataops_incidents_open
dataops_source_freshness_days
dataops_source_freshness_limit_days
dataops_source_current
```

## Production stack

| Layer | Technology |
|---|---|
| Control-plane API | Python / FastAPI |
| Hosting | Google Cloud Run |
| AdStream telemetry | Hosted FastAPI API |
| Economic-platform telemetry | Google BigQuery |
| Persistent operational state | PostgreSQL / Supabase |
| Local persistence fallback | SQLite |
| Metrics | Prometheus-compatible exposition |
| Dashboard | HTML / CSS / JavaScript |
| Containers | Docker |
| Infrastructure as Code | Terraform |
| CI | GitHub Actions |
| Testing | pytest |

## Repository map

```text
.
├── dashboard/                 # Operations dashboard
├── infra/terraform/           # Infrastructure as Code
├── operations/                # SLOs, runbooks, incidents, DR, backfill
├── prometheus/                # Metrics configuration
├── src/control_plane/
│   ├── adapters/              # Platform-specific telemetry adapters
│   ├── api.py                 # FastAPI control-plane API
│   ├── metrics.py             # Prometheus metrics
│   ├── models.py              # Normalized operational model
│   ├── observations.py        # Local observation persistence
│   └── postgres_observations.py
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.api.txt
```

## Local development

Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
pytest -q
```

Run the API:

```bash
export GCP_PROJECT_ID="<gcp-project>"
export ADSTREAM_URL="<adstream-api-url>"

uvicorn src.control_plane.api:create_app \
  --factory \
  --host 127.0.0.1 \
  --port 8020
```

Without `DATAOPS_POSTGRES_URL`, local development can use the local persistence implementation.

## Production configuration

Cloud Run uses:

```text
GCP_PROJECT_ID
ADSTREAM_URL
DATAOPS_POSTGRES_URL
```

`DATAOPS_POSTGRES_URL` is injected from **Google Secret Manager** rather than stored in Git or baked into the container image.

The runtime identity receives only the BigQuery and secret access required by the service.

## Engineering safeguards

The repository includes more than the happy path:

- automated tests for platform adapters and observation behavior;
- Dockerized runtime;
- GitHub Actions CI;
- Terraform validation;
- Prometheus-compatible metrics;
- explicit SLO documentation;
- incident-response runbook;
- backfill procedure;
- disaster-recovery guidance;
- deliberate outage and recovery testing.

See [`operations/`](operations/) for the operational documentation.

## Design principles

**Fail independently.** A source-platform outage must not become a control-plane outage.

**Preserve context.** Losing telemetry should not erase the last useful observation.

**Normalize at the boundary.** Platform-specific schemas are translated before reaching consumers.

**Keep source systems authoritative.** The control plane owns operational observations, not business data.

**Use infrastructure proportionally.** Managed services are used where they improve reliability — not simply to maximize the technology count.

## What this project demonstrates

This repository focuses on the gap between **building data pipelines** and **operating data platforms**.

It demonstrates:

- multi-platform observability;
- operational data modelling;
- managed cloud deployment;
- resilient adapter design;
- persistent health observations;
- incident detection and recovery;
- data freshness contracts;
- Prometheus instrumentation;
- Dockerized serving;
- infrastructure as code;
- CI validation;
- runbooks, SLOs, backfill, and disaster-recovery thinking.

---

## Status

### v1.0 — Feature complete

**Two independent data platforms → one resilient operational control plane.**

The core project scope is complete. The result is less about building another dashboard and more about demonstrating the engineering required to **operate data systems once they are in production**.
