resource "kubernetes_namespace" "tests" {
  metadata {
    name = var.tests_namespace
  }
}

module "litmuschaos" {
  source = "./litmuschaos"

  # depends_on = [module.litmuschaos]
}

module "chaos_pod_delete" {
  count           = var.enable_chaos_pod_delete ? 1 : 0
  source          = "./chaos-pod-delete"
  depends_on_crds = module.litmuschaos.litmus_crds_ready

  depends_on = [module.litmuschaos]
}

module "chaos_network_latency" {
  count           = var.enable_chaos_network_latency ? 1 : 0
  source          = "./chaos-network-latency"
  depends_on_crds = module.litmuschaos.litmus_crds_ready

  # depends_on = [module.litmuschaos]
}

module "chaos_cpu_stress" {
  count           = var.enable_chaos_cpu_stress ? 1 : 0
  source          = "./chaos-cpu-stress"
  depends_on_crds = module.litmuschaos.litmus_crds_ready

  # depends_on = [module.litmuschaos]
}

module "chaos_disk_stress" {
  count           = var.enable_chaos_disk_stress ? 1 : 0
  source          = "./chaos-disk-stress"
  depends_on_crds = module.litmuschaos.litmus_crds_ready

  # depends_on = [module.litmuschaos]
}

module "chaos_memory_stress" {
  count           = var.enable_chaos_memory_stress ? 1 : 0
  source          = "./chaos-memory-stress"
  depends_on_crds = module.litmuschaos.litmus_crds_ready

  # depends_on = [module.litmuschaos]
}

module "chaos_engine_pod_delete" {
  count = var.enable_chaos_pod_delete ? 1 : 0
  source = "./chaos-engine"
  chaos_engine_name = "wazuh-pod-delete-chaos"
  app_namespace = var.namespace
  app_label = var.wazuh_app_label
  experiment_name = module.chaos_pod_delete[0].experiment_name
  chaos_service_account = var.chaos_service_account
  depends_on = [module.chaos_pod_delete]
}

module "chaos_engine_network_latency" {
  count = var.enable_chaos_network_latency ? 1 : 0
  source = "./chaos-engine"
  chaos_engine_name = "wazuh-network-latency-chaos"
  app_namespace = var.namespace
  app_label = var.wazuh_app_label
  experiment_name = module.chaos_network_latency[0].experiment_name
  chaos_service_account = var.chaos_service_account
  depends_on = [module.chaos_network_latency]
}

module "chaos_engine_cpu_stress" {
  count = var.enable_chaos_cpu_stress ? 1 : 0
  source = "./chaos-engine"
  chaos_engine_name = "wazuh-cpu-stress-chaos"
  app_namespace = var.namespace
  app_label = var.wazuh_app_label
  experiment_name = module.chaos_cpu_stress[0].experiment_name
  chaos_service_account = var.chaos_service_account
  depends_on = [module.chaos_cpu_stress]
}

module "chaos_engine_disk_stress" {
  count = var.enable_chaos_disk_stress ? 1 : 0
  source = "./chaos-engine"
  chaos_engine_name = "wazuh-disk-stress-chaos"
  app_namespace = var.namespace
  app_label = var.wazuh_app_label
  experiment_name = module.chaos_disk_stress[0].experiment_name
  chaos_service_account = var.chaos_service_account
  depends_on = [module.chaos_disk_stress]
}

module "chaos_engine_memory_stress" {
  count = var.enable_chaos_memory_stress ? 1 : 0
  source = "./chaos-engine"
  chaos_engine_name = "wazuh-memory-stress-chaos"
  app_namespace = var.namespace
  app_label = var.wazuh_app_label
  experiment_name = module.chaos_memory_stress[0].experiment_name
  chaos_service_account = var.chaos_service_account
  depends_on = [module.chaos_memory_stress]
}
