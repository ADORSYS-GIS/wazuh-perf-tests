variable "namespace" {
  description = "Kubernetes namespace to deploy the CPU stress job."
  type        = string
}

variable "config" {
  description = "Optional configuration for the CPU stress job."
  type = object(
    {
      image          = optional(string, "polinux/stress")
      args           = optional(list(string), ["--cpu", "1", "--timeout", "60s"])
      back_off_limit = optional(number, 0)
    }
  )
  default = {}
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
