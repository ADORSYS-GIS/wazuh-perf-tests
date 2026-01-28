variable "app_namespace" {
  description = "The namespace of the application being targeted by the chaos experiment."
  type        = string
  default     = "wazuh"
}

variable "depends_on_crds" {
  type = any
}

variable "app_label" {
  description = "Label used to identify the application pods"
  type        = string
}

variable "chaos_service_account" {
  description = "Service account for LitmusChaos experiments"
  type        = string
}
