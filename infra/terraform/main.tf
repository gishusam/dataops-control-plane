provider "docker" {}

resource "docker_network" "dataops" {
  name = "dataops-control-plane"
}

resource "docker_image" "prometheus" {
  name         = "prom/prometheus:v2.55.1"
  keep_locally = true
}

resource "docker_image" "grafana" {
  name         = "grafana/grafana:11.2.2"
  keep_locally = true
}

resource "docker_container" "prometheus" {
  name  = "dataops-prometheus-tf"
  image = docker_image.prometheus.image_id

  networks_advanced {
    name = docker_network.dataops.name
  }

  ports {
    internal = 9090
    external = var.prometheus_port
  }

  volumes {
    host_path      = abspath("${path.module}/../../prometheus/prometheus.yml")
    container_path = "/etc/prometheus/prometheus.yml"
    read_only      = true
  }
}

resource "docker_container" "grafana" {
  name  = "dataops-grafana-tf"
  image = docker_image.grafana.image_id

  networks_advanced {
    name = docker_network.dataops.name
  }

  ports {
    internal = 3000
    external = var.grafana_port
  }

  env = [
    "GF_SECURITY_ADMIN_USER=${var.grafana_admin_user}",
    "GF_SECURITY_ADMIN_PASSWORD=${var.grafana_admin_password}"
  ]

  volumes {
    host_path      = abspath("${path.module}/../../grafana/provisioning")
    container_path = "/etc/grafana/provisioning"
    read_only      = true
  }

  volumes {
    host_path      = abspath("${path.module}/../../grafana/dashboards")
    container_path = "/var/lib/grafana/dashboards"
    read_only      = true
  }

  depends_on = [
    docker_container.prometheus
  ]
}
