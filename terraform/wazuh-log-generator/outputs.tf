output "deployment_name" {
  description = "The name of the wazuh-log-generator deployment."
  value       = kubernetes_deployment.wazuh_log_generator.metadata.name
}