module "disk_stress_experiment" {
  source = "../chaos-experiment"

  name            = "disk-stress"
  experiment_yaml = file("${path.module}/disk-stress.yaml")

  depends_on_crds = var.depends_on_crds
}
