variable "release_name" {
  description = "Helm release name for LitmusChaos"
  type        = string
  default     = "litmus"
}

variable "litmus_project_name" {
  description = "Name of the LitmusChaos project to create"
  type        = string
  default     = "default-project"
}

variable "litmus_admin_username" {
  description = "LitmusChaos admin username"
  type        = string
  default     = "admin"
}

variable "litmus_admin_password" {
  description = "LitmusChaos admin password"
  type        = string
  sensitive   = true
  default     = "litmus"
}


variable "namespace" {
  description = "Kubernetes namespace where LitmusChaos will be installed"
  type        = string
  default     = "litmus"
}
