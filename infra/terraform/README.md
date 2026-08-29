# Terraform

This Terraform configuration recreates the local DataOps monitoring environment.

It provisions:
- a dedicated Docker network;
- Prometheus;
- Grafana;
- Grafana datasource/dashboard provisioning mounts.

## Validate

```bash
terraform init
terraform fmt -check
terraform validate
```
