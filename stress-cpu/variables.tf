variable "namespace" {
  description = "Kubernetes namespace to deploy the CPU stress job."
  type        = string
}

variable "config" {
  description = "Optional configuration for the CPU stress job."
  type        = object(
    {
      image     = optional(string, "polinux/stress")
      args      = optional(list(string), ["--cpu", "1", "--timeout", "60s"])
      back_off_limit = optional(number, 0)
    }
  )
  default     = {}
}