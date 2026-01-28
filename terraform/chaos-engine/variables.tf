variable "chaos_engine_name" {
  description = "The name of the ChaosEngine resource."
  type        = string
}

variable "app_namespace" {
  description = "The namespace of the application being targeted by the chaos experiment."
  type        = string
}

variable "app_label" {
  description = "The label of the application being targeted."
  type        = string
}

variable "experiment_name" {
  description = "The name of the ChaosExperiment to be executed."
  type        = string
}

variable "chaos_service_account" {
  description = "The name of the service account to be used by the ChaosEngine."
  type        = string
}