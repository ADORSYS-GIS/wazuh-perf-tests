variable "namespace" {
  description = "The namespace to deploy the chaos experiment to."
  type        = string
  default     = "tests"
}

variable "target_namespace" {
  description = "The namespace to run the chaos experiment against."
  type        = string
  default     = "wazuh"
}

variable "release_name" {
  description = "The name of the helm release."
  type        = string
  default     = "chaos-mesh"
}

variable "latency" {
  description = "The latency to inject."
  type        = string
  default     = "100ms"
}

variable "duration" {
  description = "The duration of the chaos experiment."
  type        = string
  default     = "60s"
}

variable "enable_chaos_service_account" {
  description = "Enable the creation of a service account for chaos mesh."
  type        = bool
  default     = false
}

variable "action" {
  description = "The action to perform."
  type        = string
  default     = "delay"
}

variable "mode" {
  description = "The mode of the chaos experiment."
  type        = string
  default     = "all"
}