resource "google_bigquery_dataset" "apache_github_actions_stats" {
  dataset_id                  = "apache_github_actions_stats"
  location                    = "US"
}

resource "google_bigquery_table" "simple_statistics" {
  dataset_id = google_bigquery_dataset.apache_github_actions_stats.dataset_id
  table_id   = "simple_statistics"

  schema = <<EOF
[
  {
    "name": "repository_owner",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "repository_name",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "queued",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "in_progress",
    "type": "INTEGER",
    "mode": "NULLABLE"
  },
  {
    "name": "timestamp",
    "type": "TIMESTAMP",
    "mode": "NULLABLE"
  }
]
EOF

}
