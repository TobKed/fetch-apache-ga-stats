resource "google_service_account" "ga_actions_sa" {
  account_id   = var.service_account_name
  display_name = "GitHub Actions Service Account - upsert statistics"
}

resource "google_service_account_key" "ga_actions_sa_key" {
  service_account_id = google_service_account.ga_actions_sa.name
}

resource "local_file" "ga_actions_sa_key" {
    content     = base64decode(google_service_account_key.ga_actions_sa_key.private_key)
    filename = "${path.module}/ga_actions_sa_key.json"
}

resource "google_bigquery_dataset_iam_binding" "bq_iam_binding_data_owner" {
  project = google_bigquery_table.simple_statistics.project
  dataset_id = google_bigquery_table.simple_statistics.dataset_id
#  table_id = google_bigquery_table.simple_statistics.table_id
  role = "roles/bigquery.dataOwner"

  members = [
    "serviceAccount:${google_service_account.ga_actions_sa.email}",
  ]

  depends_on = [google_service_account.ga_actions_sa]
}

resource "google_project_iam_binding" "iam_binding_job_user" {
  project = google_bigquery_table.simple_statistics.project
#  dataset_id = google_bigquery_table.simple_statistics.dataset_id
##  table_id = google_bigquery_table.simple_statistics.table_id
  role = "roles/bigquery.user"

  members = [
    "serviceAccount:${google_service_account.ga_actions_sa.email}",
  ]

  depends_on = [google_service_account.ga_actions_sa]
}
