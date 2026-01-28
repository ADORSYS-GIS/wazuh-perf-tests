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

variable "runtime_environment" {
  description = "Runtime environment"
  type        = string
}

variable "runtime_socket_path" {
  description = "Runtime environment socker path"
  type        = string
}
