module "cpu_stress_experiment" {
  source = "../chaos-experiment"

  name                  = "cpu-stress"
  experiment_yaml       = file("${path.module}/cpu-stress.yaml")
  chaos_engine_name     = "${var.app_namespace}-cpu-stress-chaos"
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on_crds = var.depends_on_crds
}
