variable "kube_config_path" {
  description = "Path to the Kubernetes config file. Can be set with KUBE_CONFIG_PATH environment variable."
  type        = string
  default     = "~/.kube/k3s.yaml"
}

variable "kube_config_context" {
  description = "Context to use from the Kubernetes config file. Can be set with KUBE_CONFIG_CONTEXT environment variable."
  type        = string
  default     = null
}

variable "enable_chaos_pod_delete" {
  description = "Enable the LitmusChaos Pod Delete experiment"
  type        = bool
  default     = false
}

variable "enable_chaos_network_latency" {
  description = "Enable the LitmusChaos Network Latency experiment"
  type        = bool
  default     = false
}

variable "enable_chaos_cpu_stress" {
  description = "Enable the LitmusChaos CPU Stress experiment"
  type        = bool
  default     = false
}

variable "enable_chaos_disk_stress" {
  description = "Enable the LitmusChaos Disk Stress experiment"
  type        = bool
  default     = false
}

variable "enable_chaos_memory_stress" {
  description = "Enable the LitmusChaos Memory Stress experiment"
  type        = bool
  default     = false
}

variable "enable_litmuschaos" {
  description = "Enable the LitmusChaos framework installation"
  type        = bool
  default     = true
}

variable "app_namespace" {
  description = "Kubernetes namespace where the Wazuh application is deployed"
  type        = string
  default     = "wazuh"
}

variable "app_label" {
  description = "Label used to identify the Wazuh application pods"
  type        = string
  default     = "app.kubernetes.io/name=wazuh-helm"
}

variable "chaos_service_account" {
  description = "Service account for LitmusChaos experiments"
  type        = string
  default     = "litmus"
}

variable "project_id" {
  description = "Project ID for LitmusChaos"
  type        = string
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

variable "litmus_namespace" {
  description = "Kubernetes namespace where LitmusChaos will be installed"
  type        = string
  default     = "litmus"
}
