resource "kubernetes_config_map" "loggen_script" {
  metadata {
    name      = "loggen-script"
    namespace = var.namespace
  }

  data = {
    "loggen.py" = <<EOF
import time
while True:
    print('Generating logs...')
    time.sleep(1)
EOF
  }
}

resource "kubernetes_deployment" "wazuh_log_generator" {
  metadata {
    name      = "wazuh-log-generator"
    namespace = var.namespace
  }

  spec {
    replicas = var.config.replicas
    selector {
      match_labels = {
        app = "wazuh-log-generator"
      }
    }
    template {
      metadata {
        labels = {
          app = "wazuh-log-generator"
        }
      }
      spec {
        container {
          name    = "log-generator"
          image   = var.config.image
          command = var.config.command
          volume_mount {
            name       = "loggen-script-volume"
            mount_path = "/app"
          }
        }
        volume {
          name = "loggen-script-volume"
          config_map {
            name = kubernetes_config_map.loggen_script.metadata[0].name
          }
        }
      }
    }
  }
}