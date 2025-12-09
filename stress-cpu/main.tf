resource "kubernetes_job" "cpu_stress" {
  metadata {
    name      = "cpu-stress"
    namespace = var.namespace
  }

  spec {
    template {
      metadata {
        labels = {
          app = "cpu-stress"
        }
      }
      spec {
        container {
          name    = "stress"
          image   = var.config.image
          args    = var.config.args
        }
        restart_policy = "Never"
      }
    }
    backoff_limit = var.config.back_off_limit
  }
}