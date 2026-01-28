variable "depends_on_crds" {
  type = any
}

variable "app_label" {
  description = "Label used to identify the Wazuh application pods"
  type        = string
}

variable "chaos_service_account" {
  description = "Service account for LitmusChaos experiments"
  type        = string
}

variable "app_namespace" {
  description = "The namespace of the application being targeted by the chaos experiment."
  type        = string
}
