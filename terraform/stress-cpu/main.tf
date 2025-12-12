resource "kubernetes_config_map" "stress_script" {
  metadata {
    name      = "stress-script"
    namespace = var.namespace
  }

  data = {
    "stress_script.py" = file("${path.module}/stress_script.py")
  }
}

resource "kubernetes_job" "cpu_stress" {
  metadata {
    name      = "cpu-stress"
    namespace = var.namespace
  }

  wait_for_completion = false

  spec {
    backoff_limit = local.stress_config.back_off_limit

    template {
      metadata {
        labels = {
          app = "cpu-stress"
        }
      }

      spec {
        restart_policy = "Never"

        container {
          name    = "stress"
          image   = local.stress_config.image
          command = local.stress_config.command
          args    = local.stress_config.args

          volume_mount {
            name       = "stress-script-volume"
            mount_path = "/app"
          }
        }

        volume {
          name = "stress-script-volume"
          config_map {
            name = kubernetes_config_map.stress_script.metadata[0].name
          }
        }
      }
    }
  }
}
