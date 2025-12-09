output "namespace_name" {
  description = "The name of the Kubernetes namespace created for tests"
  value       = kubernetes_namespace.tests.metadata.name
}