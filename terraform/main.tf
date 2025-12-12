terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kube_config_path
  config_context = var.kube_config_context
}

provider "helm" {
  kubernetes {
    config_path    = var.kube_config_path
    config_context = var.kube_config_context
  }
}

resource "helm_release" "chaos_mesh" {
  name             = "chaos-mesh"
  repository       = "https://charts.chaos-mesh.org"
  chart            = "chaos-mesh"
  namespace        = "chaos-mesh"
  create_namespace = true
  version          = "2.6.3" # Pinning version for stability
  wait             = true
  timeout          = 600

  set {
    name  = "chaosDaemon.runtime"
    value = "containerd"
  }
  
  set {
    name  = "chaosDaemon.socketPath"
    value = "/var/run/k3s/containerd/containerd.sock"
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