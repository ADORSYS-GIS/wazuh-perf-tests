variable "name" {
  description = "Name of the chaos experiment resource"
  type        = string
  default     = "generic-chaos-experiment"
}

variable "namespace" {
  description = "Kubernetes namespace where the experiment will be deployed"
  type        = string
  default     = "litmus"
}

variable "experiment_yaml" {
  description = "YAML definition of the LitmusChaos experiment (as a string)"
  type        = string
}

variable "labels" {
  description = "Optional labels to apply to the experiment"
  type        = map(string)
  default     = {}
}

variable "depends_on_crds" {
  type = any
}

variable "chaos_engine_name" {
  description = "The name of the ChaosEngine resource."
  type        = string
}

variable "app_namespace" {
  description = "The namespace of the application being targeted by the chaos experiment."
  type        = string
}

variable "app_label" {
  description = "The label of the application being targeted."
  type        = string
}

variable "chaos_service_account" {
  description = "The name of the service account to be used by the ChaosEngine."
  type        = string
}
