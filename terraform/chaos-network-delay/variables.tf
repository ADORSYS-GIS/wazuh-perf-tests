variable "namespace" {
  description = "Kubernetes namespace to deploy the NetworkChaos resource."
  type        = string
}

variable "config" {
  description = "Optional configuration for the NetworkChaos resource."
  type = object(
    {
      target_namespace    = optional(string, "wazuh")
      pod_selector_labels = optional(map(string), {})
      delay_duration      = optional(string, "100ms")
    }
  )
  default = {}
}