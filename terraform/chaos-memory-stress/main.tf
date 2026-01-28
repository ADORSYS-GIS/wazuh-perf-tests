module "memory_stress_experiment" {
  source = "../chaos-experiment"

  name            = "memory-stress"
  namespace       = "litmus"
  experiment_yaml = file("${path.module}/memory-stress.yaml")

  depends_on_crds = var.depends_on_crds
}
