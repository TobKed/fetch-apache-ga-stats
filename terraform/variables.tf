variable "project_id" {
  description = "Project id"
  type        = string
}

variable "region" {
  description = "Region of the components"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "Zone of the components"
  type        = string
  default     = "us-central1-a"
}

variable "service_account_name" {
  description = "GitHub Actions Service Account - upsert statistics"
  type        = string
  default     = "ga-actions-asf-statistics"
}
