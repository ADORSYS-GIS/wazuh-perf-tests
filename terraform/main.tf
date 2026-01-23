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
    value = var.chaos_mesh_debug
  }
}

resource "kubernetes_namespace" "tests" {
  metadata {
    name = "tests"
  }
}


module "stress_cpu" {
  count            = var.enable_stress_cpu ? 1 : 0
  source           = "./stress-cpu"
  cpu_count        = var.stress_cpu_config.cpu_count
  duration_seconds = var.stress_cpu_config.duration_seconds

  namespace = kubernetes_namespace.tests.metadata[0].name
}

module "chaos_network" {
  count  = var.enable_chaos_network ? 1 : 0
  source = "./chaos-network-delay"

  namespace        = kubernetes_namespace.tests.metadata[0].name
  action           = var.chaos_network_config.action
  latency          = var.chaos_network_config.delay_duration
  duration         = var.chaos_network_config.duration
  target_namespace = var.chaos_network_config.target_namespace

  loss_percentage       = var.chaos_network_config.loss_percentage
  loss_correlation      = var.chaos_network_config.loss_correlation
  duplicate_percentage  = var.chaos_network_config.duplicate_percentage
  duplicate_correlation = var.chaos_network_config.duplicate_correlation
  corrupt_percentage    = var.chaos_network_config.corrupt_percentage
  corrupt_correlation   = var.chaos_network_config.corrupt_correlation
  bandwidth_rate        = var.chaos_network_config.bandwidth_rate
  bandwidth_limit       = var.chaos_network_config.bandwidth_limit
  bandwidth_buffer      = var.chaos_network_config.bandwidth_buffer

  depends_on = [helm_release.chaos_mesh]
}

# module "stress_disk" {
#   count            = 1
#   source           = "./stress-disk"
#   disk_size        = "1G"
#   duration_seconds = 120
#   rw_mode          = "randrw"

#   namespace = kubernetes_namespace.tests.metadata[0].name
# }

# module "stress_memory" {
#   count            = 1
#   source           = "./stress-memory"
#   memory_workers   = 1
#   memory_size      = "256M"
#   duration_seconds = 120

#   namespace = kubernetes_namespace.tests.metadata[0].name
# }

# module "stress_network" {
#   count            = 1
#   source           = "./stress-network"
#   duration_seconds = 120

#   namespace = kubernetes_namespace.tests.metadata[0].name
# }

