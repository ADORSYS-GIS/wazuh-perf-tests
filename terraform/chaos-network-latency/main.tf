module "network_latency_experiment" {
  source = "../chaos-experiment"

  name            = "network-latency"
  experiment_yaml = file("${path.module}/network-latency.yaml")

  depends_on_crds = var.depends_on_crds
}
