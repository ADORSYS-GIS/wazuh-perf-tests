locals {
  service_account_name = try("account-cluster-manager-${random_id.suffix[0].hex}", "account-cluster-manager")
}

resource "random_id" "suffix" {
  count       = var.enable_chaos_service_account ? 1 : 0
  byte_length = 4
}

resource "kubernetes_service_account" "chaos" {
  count = var.enable_chaos_service_account ? 1 : 0
  metadata {
    name      = local.service_account_name
    namespace = var.namespace
  }
}

resource "kubernetes_role" "chaos" {
  count = var.enable_chaos_service_account ? 1 : 0
  metadata {
    name      = "chaos-mesh-role"
    namespace = var.namespace
  }

  rule {
    api_groups = [""]
    resources  = ["pods"]
    verbs      = ["get", "watch", "list"]
  }

  rule {
    api_groups = ["chaos-mesh.org"]
    resources  = ["networkchaos"]
    verbs      = ["create", "delete", "get", "list", "watch", "patch", "update"]
  }
}

resource "kubernetes_role_binding" "chaos" {
  count = var.enable_chaos_service_account ? 1 : 0
  metadata {
    name      = "chaos-mesh-role-binding"
    namespace = var.namespace
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.chaos[0].metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.chaos[0].metadata[0].name
    namespace = var.namespace
  }
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
  depends_on = [kubernetes_role_binding.chaos]
}