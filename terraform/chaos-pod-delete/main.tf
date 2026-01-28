module "pod_delete_experiment" {
  source = "../chaos-experiment"

  name                  = "pod-delete"
  namespace             = "litmus"
  experiment_yaml       = file("${path.module}/pod-delete.yaml")
  chaos_engine_name     = "${var.app_namespace}-pod-delete-chaos"
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on_crds = var.depends_on_crds
}
