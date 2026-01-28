output "experiment_name" {
  value       = kubectl_manifest.chaos_experiment.name
  description = "The name of the Kubernetes chaos experiment resource."
}
