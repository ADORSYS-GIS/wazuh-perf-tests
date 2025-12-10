resource "kubernetes_manifest" "network_chaos" {
  depends_on = [] # Placeholder for potential future dependencies


  manifest = {
    apiVersion = "chaos-mesh.org/v1alpha1"
    kind       = "NetworkChaos"
    metadata = {
      name      = "network-delay-chaos"
      namespace = var.namespace
    }
    spec = {
      action = "delay"
      mode   = "all"
      selector = {
        namespaces = [
          var.config.target_namespace
        ]
        labelSelectors = length(var.config.pod_selector_labels) > 0 ? var.config.pod_selector_labels : null
      }
      delay = {
        latency = var.config.delay_duration
      }
      duration = "60s" # Default duration for chaos
    }
  }
}