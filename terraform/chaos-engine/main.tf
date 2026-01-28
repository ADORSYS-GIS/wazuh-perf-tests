resource "kubernetes_manifest" "chaos_engine" {
  manifest = yamldecode(templatefile("${path.module}/chaos-engine.yaml", {
    chaos_engine_name     = var.chaos_engine_name
    app_namespace         = var.app_namespace
    app_label             = var.app_label
    experiment_name       = var.experiment_name
    chaos_service_account = var.chaos_service_account
  }))
}