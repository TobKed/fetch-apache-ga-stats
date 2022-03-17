terraform {
  required_version = ">= 1.1.0"
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

variable "gcp_service_list" {
  description = "The list of apis necessary for the project"
  type        = list(string)
  default = [
    "iamcredentials.googleapis.com"
  ]
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project  = var.project_id
  service  = each.key
}
