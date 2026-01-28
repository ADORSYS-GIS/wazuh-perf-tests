variable "namespace" {
  description = "Kubernetes namespace where LitmusChaos will be installed"
  type        = string
  default     = "litmus"
}

variable "litmus_admin_username" {
  description = "LitmusChaos admin username"
  type        = string
}

variable "litmus_admin_password" {
  description = "LitmusChaos admin password"
  type        = string
  sensitive   = true
}

variable "project_id" {
  description = "Project ID for LitmusChaos"
  type        = string
}

variable "infra_mode" {
  description = "Infrastructure mode for LitmusChaos (e.g., cluster, namespace)"
  type        = string
  default     = "cluster"
}

variable "platform" {
  description = "Platform where LitmusChaos is deployed (e.g., Rancher, EKS, GKE)"
  type        = string
  default     = "Rancher"
}

variable "litmus_environment" {
  description = "Environment ID for LitmusChaos"
  type        = string
}
