variable "prometheus_port" {
  description = "Host port exposed by Prometheus."
  type        = number
  default     = 9090
}

variable "grafana_port" {
  description = "Host port exposed by Grafana."
  type        = number
  default     = 3000
}

variable "grafana_admin_user" {
  description = "Initial Grafana administrator username."
  type        = string
  default     = "admin"
}

variable "grafana_admin_password" {
  description = "Initial Grafana administrator password."
  type        = string
  sensitive   = true
  default     = "admin"
}
