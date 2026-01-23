variable "namespace" {
  description = "Kubernetes namespace to deploy the CPU stress job."
  type        = string
}


variable "cpu_count" {
  description = "Number of CPU cores to stress."
  type        = number
  default     = 1
}

variable "duration_seconds" {
  description = "Duration in seconds to run the CPU stress."
  type        = number
  default     = 60
}
