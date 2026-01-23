locals {
  service_account_name = "chaos-sa"
}

resource "random_id" "suffix" {
  byte_length = 4
}

resource "kubernetes_service_account" "chaos" {
  metadata {
    name      = local.service_account_name
    namespace = var.namespace
  }
}

resource "kubernetes_role" "chaos_role" {
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

resource "kubernetes_role_binding" "chaos_rolebinding" {
  metadata {
    name      = "chaos-mesh-role-binding"
    namespace = var.namespace
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.chaos_role.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.chaos.metadata[0].name
    namespace = var.namespace
  }
}

resource "kubernetes_secret" "service_account_token" {
  metadata {
    name      = "${local.service_account_name}-token"
    namespace = var.namespace
    annotations = {
      "kubernetes.io/service-account.name" = local.service_account_name
    }
  }
  type = "kubernetes.io/service-account-token"
  wait_for_service_account_token = true
  depends_on = [kubernetes_service_account.chaos, kubernetes_role_binding.chaos_rolebinding]
}
