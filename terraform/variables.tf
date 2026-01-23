variable "kube_config_path" {
  description = "Path to the Kubernetes config file. Can be set with KUBE_CONFIG_PATH environment variable."
  type        = string
  default     = "~/.kube/k3s.yaml"
}

variable "kube_config_context" {
  description = "Context to use from the Kubernetes config file. Can be set with KUBE_CONFIG_CONTEXT environment variable."
  type        = string
  default     = null
}

variable "enable_stress_cpu" {
  description = "Enable the Stress CPU sub-module"
  type        = bool
  default     = false
}

variable "enable_chaos_network" {
  description = "Enable the Chaos Network sub-module"
  type        = bool
  default     = false
}

variable "wazuh_log_generator_config" {
  description = "Configuration for the Wazuh Log Generator sub-module"
  type = object(
    {
      log_script_content = optional(string, "print('Generating logs...')")
      image              = optional(string, "python:3.9-slim-buster")
      command            = optional(list(string), ["python", "/app/loggen.py"])
      replicas           = optional(number, 1)
    }
  )
  default = {}
}

variable "stress_cpu_config" {
  description = "Configuration for the Stress CPU sub-module"
  type = object(
    {
      cpu_count        = optional(number, 1)
      duration_seconds = optional(number, 60)
    }
  )
  default = {}
}

variable "chaos_network_config" {
  description = "Configuration for the Chaos Network sub-module"
  type = object(
    {
      enable_service_account = optional(bool, false)
      action                = optional(string, "delay")
      target_namespace      = optional(string, "wazuh")
      pod_selector_labels   = optional(map(string), {})
      delay_duration        = optional(string, "100ms")
      duration              = optional(string, "120s")
      loss_percentage       = optional(string)
      loss_correlation      = optional(string)
      duplicate_percentage  = optional(string)
      duplicate_correlation = optional(string)
      corrupt_percentage    = optional(string)
      corrupt_correlation   = optional(string)
      bandwidth_rate        = optional(string)
      bandwidth_limit       = optional(string)
      bandwidth_buffer      = optional(string)
    }
  )
  default = {}
}

variable "chaos_daemon_socket_path" {
  description = "Socket path for the Chaos Daemon"
  type        = string
  default     = "/var/run/containerd/containerd.sock"
}

variable "chaos_daemon_runtime" {
  description = "Container runtime for the Chaos Daemon"
  type        = string
  default     = "containerd"
}

variable "chaos_mesh_debug" {
  description = "Enable debug mode for Chaos Mesh"
  type        = bool
  default     = true
}
