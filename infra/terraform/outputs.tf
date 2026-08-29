output "prometheus_url" {
  description = "Local Prometheus URL."
  value       = "http://localhost:${var.prometheus_port}"
}

output "grafana_url" {
  description = "Local Grafana URL."
  value       = "http://localhost:${var.grafana_port}"
}
