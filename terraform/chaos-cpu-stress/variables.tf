variable "namespace" {
  description = "Kubernetes namespace where the experiment will be deployed"
  type        = string
  default     = "litmus"
}

variable "depends_on_crds" {
  type = any
}