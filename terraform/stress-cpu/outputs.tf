output "job_name" {
  description = "The name of the cpu-stress job."
  value       = kubernetes_job.cpu_stress.metadata.name
}