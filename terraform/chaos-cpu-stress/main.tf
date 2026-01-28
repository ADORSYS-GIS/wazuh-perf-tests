module "cpu_stress_experiment" {
  source = "../chaos-experiment"

  name            = "cpu-stress"
  experiment_yaml = file("${path.module}/cpu-stress.yaml")

  depends_on_crds = var.depends_on_crds
}
