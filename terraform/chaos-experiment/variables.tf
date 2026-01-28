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