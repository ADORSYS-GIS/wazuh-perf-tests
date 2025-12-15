output "network_chaos_name" {
  description = "The name of the NetworkChaos resource."
  value       = kubernetes_manifest.network_chaos.manifest.metadata.name
}

output "service_account_name" {
  description = "The name of the ServiceAccount token request."
  value       = var.enable_chaos_service_account ? kubernetes_token_request_v1.service_account_token[0].metadata[0].name : null
}

output "service_account_token" {
  description = "The token generated for the ServiceAccount."
  value       = var.enable_chaos_service_account ? kubernetes_token_request_v1.service_account_token[0].token : null
  sensitive   = true
}
