module "pod_delete_experiment" {
  source = "../chaos-experiment"

  name            = "pod-delete"
  namespace       = "litmus"
  experiment_yaml = file("${path.module}/pod-delete.yaml")

  depends_on_crds = var.depends_on_crds
}
