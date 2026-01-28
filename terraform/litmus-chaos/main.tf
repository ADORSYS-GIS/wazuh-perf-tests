resource "helm_release" "litmus" {
  name             = "${var.namespace}-chaos"
  repository       = "https://litmuschaos.github.io/litmus-helm"
  chart            = "litmus"
  namespace        = var.namespace
  create_namespace = true
  version          = "3.24.0"
  timeout          = 900
  wait             = true
  wait_for_jobs    = true

  set {
    name  = "installCRDs"
    value = "false"
  }

  set {
    name  = "portal.frontend.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "mongodb.enabled"
    value = "true"
  }

  set {
    name  = "mongodb.auth.enabled"
    value = "true"
  }

  set {
    name  = "server.waitForMongodb.enabled"
    value = "true"
  }

  set {
    name  = "adminConfig.ADMIN_USERNAME"
    value = var.litmus_admin_username
  }

  set {
    name  = "adminConfig.ADMIN_PASSWORD"
    value = var.litmus_admin_password
  }

}

# resource "helm_release" "litmus_experiments" {
#   name             = "${var.namespace}-experiments"
#   repository       = "https://litmuschaos.github.io/litmus-helm"
#   chart            = "kubernetes-chaos"
#   namespace        = var.namespace
#   create_namespace = true
#   version          = "3.25.0"
#   timeout          = 300
#   wait             = true

#   set {
#     name  = "environment.runtime"
#     value = var.runtime_environment
#   }

#   set {
#     name  = "environment.socketPath"
#     value = var.runtime_socket_path
#   }

#   set {
#     name  = "installCRDs"
#     value = "true"
#   }

#   depends_on = [helm_release.litmus]
# }
