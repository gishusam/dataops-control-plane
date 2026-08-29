# Incident History

## INC-001 — AdStream unavailable

**Status:** Demonstration incident

### Impact

AdStream operational telemetry became unavailable to the DataOps Control Plane.

Kenya Economic and the Control Plane remained operational.

### Detection

Prometheus reported:

`dataops_platform_up{platform="adstream"} = 0`

The Control Plane reported:

`dataops_incidents_open{platform="adstream"} = 1`

Grafana displayed AdStream as unavailable.

### Root cause

The AdStream API process was intentionally stopped during control-plane validation.

### Control Plane behavior

The AdStream adapter returned a normalized unavailable state instead of propagating the HTTP connection failure.

Monitoring for Kenya Economic continued normally.

### Data loss

None.

### Recovery

Restart the AdStream API and confirm the next Prometheus scrape changes:

`dataops_platform_up{platform="adstream"}: 0 -> 1`

and:

`dataops_incidents_open{platform="adstream"}: 1 -> 0`

### Lesson

Monitoring infrastructure must remain operational when the system being monitored fails.
