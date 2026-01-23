resource "time_sleep" "wait_for_chaos_mesh" {
  create_duration = "30s"

  triggers = {
    "release_name" = var.release_name
  }
}

locals {
  delay_spec     = var.action == "delay" ? { "delay" = { "latency" = var.latency } } : {}
  loss_spec      = var.action == "loss" ? { "loss" = { "loss" = var.loss_percentage, "correlation" = var.loss_correlation } } : {}
  duplicate_spec = var.action == "duplicate" ? { "duplicate" = { "duplicate" = var.duplicate_percentage, "correlation" = var.duplicate_correlation } } : {}
  corrupt_spec   = var.action == "corrupt" ? { "corrupt" = { "corrupt" = var.corrupt_percentage, "correlation" = var.corrupt_correlation } } : {}
  bandwidth_spec = var.action == "bandwidth" ? { "bandwidth" = { "rate" = var.bandwidth_rate, "limit" = var.bandwidth_limit, "buffer" = coalesce(var.bandwidth_buffer, 0) == 0 ? 1 : var.bandwidth_buffer } } : {}
  partition_spec = {} # Partition action doesn't require a separate spec block

  base_spec = {
    "action" = var.action
    "mode"   = var.mode
    "selector" = {
      "namespaces" = [var.namespace]
    }
    "duration" = var.duration
  }

  final_spec = merge(
    local.base_spec,
    local.delay_spec,
    local.loss_spec,
    local.duplicate_spec,
    local.corrupt_spec,
    local.bandwidth_spec,
    local.partition_spec
  )
}

resource "null_resource" "action_trigger" {
  triggers = {
    action = var.action
  }
}

// remove_finalizer resource removed as finalizer handling omitted

// Removed clear_finalizer and log_finalizer resources as finalizer handling is omitted

resource "kubernetes_manifest" "network_chaos" {
  depends_on = [time_sleep.wait_for_chaos_mesh]

  manifest = {
    "apiVersion" = "chaos-mesh.org/v1alpha1"
    "kind"       = "NetworkChaos"
    "metadata" = {
      "name"        = "network-delay-chaos"
      "namespace"   = var.namespace
      # finalizers omitted to avoid provider inconsistency
    }
    "spec" = local.final_spec
  }

  lifecycle {
    replace_triggered_by = [null_resource.action_trigger]
  }
}
