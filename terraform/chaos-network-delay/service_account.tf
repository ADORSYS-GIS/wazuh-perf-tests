locals {
  service_account_name = try("account-cluster-manager-${random_id.suffix[0].hex}", "account-cluster-manager")
}

resource "random_id" "suffix" {
  count       = var.enable_chaos_service_account ? 1 : 0
  byte_length = 4
}

data "template_file" "rbac" {
  count    = var.enable_chaos_service_account ? 1 : 0
  template = file("${path.module}/templates/rbac.yaml")
  vars = {
    namespace            = var.namespace
    service_account_name = local.service_account_name
  }
}

resource "kubernetes_manifest" "rbac" {
  count    = var.enable_chaos_service_account ? 1 : 0
  manifest = yamldecode(data.template_file.rbac[0].rendered)
}

resource "kubernetes_token_request_v1" "service_account_token" {
  count = var.enable_chaos_service_account ? 1 : 0
  metadata {
    name      = "${local.service_account_name}-token"
    namespace = var.namespace
  }
  spec {
    audiences          = ["api"]
    expiration_seconds = 86400
    bound_object_ref {
      kind        = "ServiceAccount"
      name        = local.service_account_name
      api_version = "v1"
    }
  }
  depends_on = [kubernetes_manifest.rbac]
}