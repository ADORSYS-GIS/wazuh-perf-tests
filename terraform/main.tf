resource "helm_release" "chaos_mesh" {
  name             = "chaos-mesh"
  repository       = "https://charts.chaos-mesh.org"
  chart            = "chaos-mesh"
  namespace        = "chaos-mesh"
  create_namespace = true
  version          = "2.6.3" # Pinning version for stability
  wait             = false
  timeout          = 600

  set {
    name  = "chaosDaemon.runtime"
    value = var.chaos_daemon_runtime
  }

  set {
    name  = "chaosDaemon.socketPath"
    value = var.chaos_daemon_socket_path
  }

  set {
    name  = "debug"
    value = "true"
  }
}

resource "kubernetes_namespace" "tests" {
  metadata {
    name = "tests"
  }
}


module "stress_cpu" {
  count  = var.enable_stress_cpu ? 1 : 0
  source = "./stress-cpu"

  namespace = kubernetes_namespace.tests.metadata[0].name
  config    = var.stress_cpu_config
}

module "chaos_network_delay" {
  count  = var.enable_chaos_network_delay ? 1 : 0
  source = "./chaos-network-delay"

  namespace = kubernetes_namespace.tests.metadata[0].name
  config    = var.chaos_network_delay_config

  depends_on = [helm_release.chaos_mesh]
}

output "namespace_name" {
  description = "The name of the Kubernetes namespace created for tests"
  value       = kubernetes_namespace.tests.metadata[0].name
}
