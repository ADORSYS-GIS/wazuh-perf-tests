variable "namespace" {
  description = "Kubernetes namespace to deploy the log generator."
  type        = string
}

variable "config" {
  description = "Optional configuration for the log generator."
  type        = object(
    {
      log_script_content = optional(string, "print('Generating logs...')")
      image              = optional(string, "python:3.9-slim-buster")
      command            = optional(list(string), ["python", "/app/loggen.py"])
      replicas           = optional(number, 1)
    }
  )
  default     = {}
}