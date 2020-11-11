"""
Example use:
    gsutil -m cp -r gs://example-bucket/apache gcs

    python parse_existing_json_files.py \
        --input-dir gcs \
        --output bq_csv.csv

    bq load --autodetect \
        --source_format=CSV \
        dataset.table bq_csv.csv

"""
import argparse
import csv
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

CSV_FIELDNAMES = [
    "repository_owner",
    "repository_name",
    "queued",
    "in_progress",
    "timestamp",
]


def parse_args() -> Tuple[str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input-dir",
        help="Base directory, first folder treated as organisation (org/repo...n)",
        required=True,
    )
    parser.add_argument("--output", help="CSV output file", required=True)
    args = parser.parse_args()
    return args.input_dir, args.output


def get_stats_from_file(file: str) -> Tuple[int, int]:
    with open(file) as json_file:
        data = json.load(json_file)
    in_progress = sum(d["status"] == "in_progress" for d in data)
    queued = sum(d["status"] == "queued" for d in data)
    return in_progress, queued


def get_timestamp_from_filename(file: str) -> datetime:
    name = Path(file).name
    name = name[:-5]
    t = datetime.strptime(name, "%Y%m%d_%H%M%SZ")
    t.replace(tzinfo=timezone.utc)
    return t


def parse_repos(owner: str, repos_dir: str, output: str) -> None:
    with open(output, mode="w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        failed = []
        for repo in os.listdir(repos_dir):
            repo_dir = os.path.join(repos_dir, repo)
            files = [
                os.path.join(repo_dir, p)
                for p in os.listdir(repo_dir)
                if p.endswith(".json")
            ]

            for file in files:
                try:
                    in_progress, queued = get_stats_from_file(file)
                    timestamp = get_timestamp_from_filename(file)
                    csv_data = {
                        "repository_name": repo,
                        "repository_owner": owner,
                        "queued": in_progress,
                        "in_progress": queued,
                        "timestamp": timestamp,
                    }
                    print(f"{owner}/{repo}: {in_progress}, {queued}")
                    writer.writerow(csv_data)
                except:  # noqa
                    failed.append(file)

    print(f"Failed files {len(failed)}:")
    for f in failed:
        print(f)


if __name__ == "__main__":
    base_dir, output = parse_args()

    owners = os.listdir(base_dir)
    if owners and len(owners) == 1:
        owner = owners[0]
        repos_dir = os.path.join(base_dir, owner)
        parse_repos(owner, repos_dir, output)
    elif owners:
        for owner in os.listdir(base_dir):
            repos_dir = os.path.join(base_dir, owner)
            parse_repos(owner, repos_dir, f"{output}_{owner}")
