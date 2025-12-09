output "network_chaos_name" {
  description = "The name of the NetworkChaos resource."
  value       = kubernetes_manifest.network_chaos.manifest.metadata.name
}