module "network_latency_experiment" {
  source = "../chaos-experiment"

  name                  = "network-latency"
  experiment_yaml       = file("${path.module}/network-latency.yaml")
  chaos_engine_name     = "${var.app_namespace}-network-latency-chaos"
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on_crds = var.depends_on_crds
}
