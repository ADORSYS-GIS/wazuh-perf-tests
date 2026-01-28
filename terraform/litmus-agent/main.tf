resource "helm_release" "litmus_agent" {
  name             = "${var.namespace}-agent"
  repository       = "litmuschaos"
  chart            = "litmus-agent"
  namespace        = var.namespace
  create_namespace = true
  version          = "3.24.0"
  timeout          = 300
  wait             = true
  wait_for_jobs    = true

  set {
    name  = "installCRDs"
    value = "false"
  }

  set {
    name  = "LITMUS_URL"
    value = "http://litmus-chaos-frontend-service.${var.namespace}.svc.cluster.local:9091"
  }

  set {
    name  = "LITMUS_BACKEND_URL"
    value = "http://litmus-chaos-server-service.${var.namespace}.svc.cluster.local:9002"

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

  set {
    name  = "LITMUS_ENVIRONMENT_ID"
    value = var.litmus_environment
  }

  set {
    name  = "INFRA_NAME"
    value = var.litmus_environment
  }
}
