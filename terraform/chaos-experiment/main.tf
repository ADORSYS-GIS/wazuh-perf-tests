resource "kubernetes_manifest" "chaos_experiment" {
  manifest = yamldecode(var.experiment_yaml)

  field_manager {
    force_conflicts = true
  }

  depends_on = [var.depends_on_crds]
}

resource "kubernetes_manifest" "chaos_engine" {
  manifest = yamldecode(templatefile("${path.module}/chaos-engine.yaml", {
    experiment_name       = var.name
    chaos_engine_name     = var.chaos_engine_name
    app_namespace         = var.app_namespace
    app_label             = var.app_label
    chaos_service_account = var.chaos_service_account
  }))
}
