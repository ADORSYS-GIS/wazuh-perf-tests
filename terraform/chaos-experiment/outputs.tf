output "experiment_name" {
  value = kubernetes_manifest.chaos_experiment.object.metadata.name
  description = "The name of the Kubernetes chaos experiment resource."
}
