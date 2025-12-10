variable "kube_config_path" {
  description = "Path to the Kubernetes config file. Can be set with KUBE_CONFIG_PATH environment variable."
  type        = string
  default     = "~/.kube/config"
}

variable "kube_config_context" {
  description = "Context to use from the Kubernetes config file. Can be set with KUBE_CONFIG_CONTEXT environment variable."
  type        = string
  default     = null
}

variable "namespace" {
  description = "Kubernetes namespace to deploy the test resources."
  type        = string
  default     = "default"
}


variable "enable_wazuh_log_generator" {
  description = "Enable the Wazuh Log Generator sub-module"
  type        = bool
  default     = false
}

variable "enable_stress_cpu" {
  description = "Enable the Stress CPU sub-module"
  type        = bool
  default     = false
}

variable "enable_chaos_network_delay" {
  description = "Enable the Chaos Network Delay sub-module"
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
      image          = optional(string, "polinux/stress")
      args           = optional(list(string), ["--cpu", "1", "--timeout", "60s"])
      back_off_limit = optional(number, 0)
    }
  )
  default = {}
}

variable "chaos_network_delay_config" {
  description = "Configuration for the Chaos Network Delay sub-module"
  type = object(
    {
      target_namespace = optional(string, "wazuh")
      pod_selector_labels = optional(map(string), {})
      delay_duration = optional(string, "100ms")
    }
  )
  default = {}
}