resource "kubernetes_manifest" "chaos_experiment" {
  manifest = yamldecode(var.experiment_yaml)

  field_manager {
    force_conflicts = true
  }

  depends_on = [var.depends_on_crds]
}
