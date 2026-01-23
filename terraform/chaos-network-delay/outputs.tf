output "network_chaos_name" {
  description = "The name of the NetworkChaos resource."
  value       = kubernetes_manifest.network_chaos.manifest.metadata.name
}

output "service_account_name" {
  description = "The name of the ServiceAccount token request."
  value       = kubernetes_secret.service_account_token.metadata[0].name
}

output "service_account_token" {
  description = "The token generated for the ServiceAccount."
  value       = kubernetes_secret.service_account_token.data["token"]
  sensitive   = true
}
