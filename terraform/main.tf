module "litmus_chaos" {
  source                = "./litmus-chaos"
  namespace             = var.litmus_namespace
  litmus_admin_username = var.litmus_admin_username
  litmus_admin_password = var.litmus_admin_password
}

module "litmus_agent" {
  source                = "./litmus-agent"
  project_id            = var.project_id
  install_crds          = true
  litmus_admin_username = var.litmus_admin_username
  litmus_admin_password = var.litmus_admin_password
  namespace             = var.litmus_namespace

  depends_on = [module.litmus_chaos]
}


module "chaos_pod_delete" {
  count                 = var.enable_chaos_pod_delete ? 1 : 0
  source                = "./chaos-pod-delete"
  depends_on_crds       = module.litmus_chaos.litmus_crds_ready
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on = [module.litmus_chaos]
}

module "chaos_network_latency" {
  count                 = var.enable_chaos_network_latency ? 1 : 0
  source                = "./chaos-network-latency"
  depends_on_crds       = module.litmus_chaos.litmus_crds_ready
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on = [module.litmus_chaos]
}

module "chaos_cpu_stress" {
  count                 = var.enable_chaos_cpu_stress ? 1 : 0
  source                = "./chaos-cpu-stress"
  depends_on_crds       = module.litmus_chaos.litmus_crds_ready
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account


  depends_on = [module.litmus_chaos]
}

module "chaos_disk_stress" {
  count                 = var.enable_chaos_disk_stress ? 1 : 0
  source                = "./chaos-disk-stress"
  depends_on_crds       = module.litmus_chaos
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on = [module.litmus_chaos]
}

module "chaos_memory_stress" {
  count                 = var.enable_chaos_memory_stress ? 1 : 0
  source                = "./chaos-memory-stress"
  depends_on_crds       = module.litmus_chaos
  app_namespace         = var.app_namespace
  app_label             = var.app_label
  chaos_service_account = var.chaos_service_account

  depends_on = [module.litmus_chaos]
}
