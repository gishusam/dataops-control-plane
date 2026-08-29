# DataOps Runbook

## Platform unavailable

1. Confirm `dataops_platform_up{platform="<name>"}` is `0`.
2. Check `dataops_incidents_open`.
3. Inspect the platform-specific operational source.
4. Identify whether the failure is:
   - connectivity;
   - pipeline execution;
   - serving readiness;
   - data freshness;
   - data quality.
5. Restore the failed dependency or service.
6. Confirm platform health returns to `1`.
7. Confirm the active incident returns to `0`.

## AdStream checks

Validate:

- `/health`
- `/ready`
- `/api/v1/pipeline-health`
- latest Airflow pipeline run
- Silver / Gold / Quality / Serving stage health
- serving database readiness

## Kenya Economic checks

Validate:

- `marts.pipeline_status`
- `marts.source_health`
- latest dbt status
- source freshness thresholds
- Cloud Run Job execution state

## Control Plane checks

Validate:

- `/health`
- `/api/v1/platforms`
- `/metrics`
- Prometheus scrape target
- Grafana datasource connectivity

The Control Plane must remain operational when one managed platform is unavailable.
