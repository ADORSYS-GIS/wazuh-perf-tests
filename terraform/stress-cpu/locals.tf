locals {
  stress_config = {
    image          = "python:3.11-slim-bullseye"
    cpu_count      = var.cpu_count
    timeout        = var.duration_seconds
    back_off_limit = 0
    command        = ["/bin/bash", "-c"]
    args = [
      "apt-get update && apt-get install -y --no-install-recommends stress && python3 /app/stress_script.py --cpu-count ${var.cpu_count} --timeout ${var.duration_seconds}"
    ]
  }
}
