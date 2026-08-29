# Disaster Recovery

## Control Plane

The Control Plane is stateless with respect to managed platform data.

Its operational state is reconstructed from:

- AdStream operational API;
- Kenya Economic BigQuery marts;
- Prometheus metrics;
- provisioned Grafana dashboards.

## Rebuild sequence

1. Restore source platform connectivity.
2. Start the Control Plane API.
3. Start Prometheus.
4. Start Grafana.
5. Verify `/metrics`.
6. Verify Prometheus targets.
7. Verify Grafana dashboards.

## Recovery principle

The Control Plane does not own business data and therefore should not become a single point of data loss.

Managed platforms remain authoritative for their own operational and analytical state.
