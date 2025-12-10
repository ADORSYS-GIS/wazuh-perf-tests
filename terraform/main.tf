terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path    = var.kube_config_path
  config_context = var.kube_config_context
}

resource "kubernetes_namespace" "tests" {
  metadata {
    name = "tests"
  }
}

module "wazuh_log_generator" {
  count  = var.enable_wazuh_log_generator ? 1 : 0
  source = "./wazuh-log-generator"

  namespace = kubernetes_namespace.tests.metadata.name
  config    = var.wazuh_log_generator_config
}

module "stress_cpu" {
  count  = var.enable_stress_cpu ? 1 : 0
  source = "./stress-cpu"

  namespace = kubernetes_namespace.tests.metadata.name
  config    = var.stress_cpu_config
}

module "chaos_network_delay" {
  count  = var.enable_chaos_network_delay ? 1 : 0
  source = "./chaos-network-delay"

  namespace = kubernetes_namespace.tests.metadata.name
  config    = var.chaos_network_delay_config
}

output "namespace_name" {
  description = "The name of the Kubernetes namespace created for tests"
  value       = kubernetes_namespace.tests.metadata.name
}