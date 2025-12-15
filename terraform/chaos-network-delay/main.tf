resource "time_sleep" "wait_for_chaos_mesh" {
  create_duration = "30s"

  triggers = {
    "release_name" = var.release_name
  }
}

resource "kubernetes_manifest" "network_chaos" {
  depends_on = [time_sleep.wait_for_chaos_mesh]

  manifest = {
    "apiVersion" = "chaos-mesh.org/v1alpha1"
    "kind"       = "NetworkChaos"
    "metadata" = {
      "name"      = "network-delay-chaos"
      "namespace" = var.namespace
    }
    "spec" = {
      "action" = "delay"
      "mode"   = "all"
      "selector" = {
        "namespaces" = [
          var.namespace
        ]
      }
      "delay" = {
        "latency" = var.latency
      }
      "duration" = var.duration
    }
  }
}
