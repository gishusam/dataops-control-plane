# DataOps Service Level Objectives

## Fleet objective

The DataOps Control Plane monitors heterogeneous data platforms through a normalized operational contract.

A failure in a managed platform must never cause the Control Plane itself to fail.

## AdStream

| Signal | Objective |
|---|---|
| Platform availability | Healthy when API, serving database, and latest pipeline run are healthy |
| Pipeline status | Latest medallion pipeline run succeeds |
| Stage observability | Silver, Gold, Quality, and Serving stages are observable |
| Recovery behavior | Platform recovery must clear the active incident automatically |
| Control Plane resilience | AdStream unavailability must not crash the Control Plane |

## Kenya Economic Platform

| Signal | Objective |
|---|---|
| Pipeline status | Latest autonomous refresh succeeds |
| dbt status | Latest dbt execution succeeds |
| CBK freshness | Age <= 4 days |
| KNBS freshness | Age <= 45 days |
| World Bank freshness | Age <= 400 days |
| Source isolation | A failed source may degrade the platform without discarding healthy source data |

## Incident semantics

- `healthy` => `0` active incidents
- `degraded` => `1` active incident
- `unavailable` => `1` active incident
