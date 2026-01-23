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

variable "loss_percentage" {
  description = "The percentage of packet loss to inject."
  type        = string
  default     = null
}

variable "loss_correlation" {
  description = "The correlation of packet loss."
  type        = string
  default     = "0"
}

variable "duplicate_percentage" {
  description = "The percentage of packet duplication to inject."
  type        = string
  default     = null
}

variable "duplicate_correlation" {
  description = "The correlation of packet duplication."
  type        = string
  default     = "0"
}

variable "corrupt_percentage" {
  description = "The percentage of packet corruption to inject."
  type        = string
  default     = null
}

variable "corrupt_correlation" {
  description = "The correlation of packet corruption."
  type        = string
  default     = "0"
}

variable "bandwidth_rate" {
  description = "The bandwidth rate limit."
  type        = string
  default     = null
}

variable "bandwidth_limit" {
  description = "The bandwidth limit."
  type        = number
  default     = 0
}

variable "bandwidth_buffer" {
  description = "The bandwidth buffer."
  type        = number
  default     = 0
}
