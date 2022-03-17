output "GCP_PROJECT_ID" {
  value = var.project_id
}

output "BQ_TABLE" {
  value = "${google_bigquery_dataset.apache_github_actions_stats.dataset_id}.${google_bigquery_table.simple_statistics.table_id}"
}

output "GCP_SA_EMAIL" {
  value = google_service_account.ga_actions_sa.email
}

output "GCP_SA_KEY_FILE" {
  value = local_file.ga_actions_sa_key.filename
}
