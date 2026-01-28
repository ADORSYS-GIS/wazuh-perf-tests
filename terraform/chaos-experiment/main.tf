resource "kubectl_manifest" "chaos_experiment" {
  yaml_body = var.experiment_yaml

  force_conflicts = true

  depends_on = [var.depends_on_crds]
}

resource "kubectl_manifest" "chaos_engine" {
  yaml_body = templatefile("${path.module}/chaos-engine.yaml", {
    experiment_name       = var.name
    chaos_engine_name     = var.chaos_engine_name
    app_namespace         = var.app_namespace
    app_label             = var.app_label
    chaos_service_account = var.chaos_service_account
  })

  force_conflicts = true

  depends_on = [var.depends_on_crds]
}
