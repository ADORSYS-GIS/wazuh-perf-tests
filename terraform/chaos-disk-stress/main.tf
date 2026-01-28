module "disk_stress_experiment" {
  source = "../chaos-experiment"

  name            = "disk-stress"
  experiment_yaml = file("${path.module}/disk-stress.yaml")

  chaos_engine_name     = "${var.app_namespace}-disk-stress-chaos"
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account


  depends_on_crds = var.depends_on_crds
}
