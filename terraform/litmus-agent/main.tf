resource "helm_release" "litmus_agent" {
  name             = "${var.namespace}-agent"
  repository       = "https://litmuschaos.github.io/litmus-helm"
  chart            = "litmus-agent"
  namespace        = var.namespace
  create_namespace = true
  version          = "3.24.0"
  timeout          = 300
  wait             = true
  skip_crds        = true

  set {
    name  = "installCRDs"
    value = var.install_crds ? "true" : "false"
  }

  set {
    name  = "LITMUS_URL"
    value = "http://litmus-frontend-service.${var.namespace}.svc.cluster.local:9091"
  }

  set {
    name  = "LITMUS_BACKEND_URL"
    value = "http://litmus-server-service.${var.namespace}.svc.cluster.local:9002"

  }

  set {
    name  = "global.INFRA_MODE"
    value = var.infra_mode
  }

  set {
    name  = "PLATFORM"
    value = var.platform
  }

  set {
    name  = "workflow-controller.crds.create"
    value = "false"
  }

  set {
    name  = "PROJECT_ID"
    value = var.project_id
  }

  set {
    name  = "LITMUS_USERNAME"
    value = var.litmus_admin_username
  }
  set {
    name  = "LITMUS_PASSWORD"
    value = var.litmus_admin_password
  }
}
