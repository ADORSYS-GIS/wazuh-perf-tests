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

  set {
    name  = "chaosDaemon.runtime"
    value = "containerd"
  }
  
  set {
    name  = "chaosDaemon.socketPath"
    value = "/run/containerd/containerd.sock"
  }
}

resource "null_resource" "wait_for_chaos_mesh" {
  depends_on = [helm_release.chaos_mesh]

  provisioner "local-exec" {
    command = "kubectl wait --for=condition=Available deployment/chaos-mesh-controller-manager -n chaos-mesh --timeout=300s && until kubectl get pods -n chaos-mesh -l app.kubernetes.io/component=chaos-daemon --field-selector=status.phase=Running --no-headers | grep 'Running'; do echo 'Waiting for chaos-daemon pods to be running...' && sleep 10; done && sleep 30"
  }

  triggers = {
    release_name = helm_release.chaos_mesh.name
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

  depends_on = [null_resource.wait_for_chaos_mesh]
}

output "namespace_name" {
  description = "The name of the Kubernetes namespace created for tests"
  value       = kubernetes_namespace.tests.metadata[0].name
}