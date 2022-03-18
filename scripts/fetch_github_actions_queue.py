# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""
Example:

    GITHUB_TOKEN=1234 python scripts/fetch_github_actions_queue.py \
        --input matrix.json \
        --bq-output ${{ env.BQ_CSV_FILE }} \
        --output-dir ${{ env.STATS_DIR }}

"""
import argparse
import csv
import json
import os
from datetime import datetime, timezone
from typing import List, Tuple

import requests

GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
REPO_WORKFLOWS_URL_FMT: str = "https://api.github.com/repos/{owner}/{repo}/actions/runs"
CSV_FIELDNAMES = [
    "repository_owner",
    "repository_name",
    "queued",
    "in_progress",
    "timestamp",
]


def parse_args() -> Tuple[str, str, str]:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", help="Json file wih organisation and repositories", required=True
    )
    parser.add_argument(
        "--bq-output", help="Single csv file for BigQuery", required=True
    )
    parser.add_argument(
        "--output-dir", help="Directory for separate json files", required=True
    )
    args = parser.parse_args()
    return args.input, args.bq_output, args.output_dir


def parse_input_file(file: str) -> Tuple[str, List[str]]:
    with open(file) as json_file:
        data = json.load(json_file)
    return data["organisation"][0], data["repository"]


def fetch_repo_queue(owner: str, repo: str) -> Tuple[list, dict, datetime]:
    timestamp = datetime.now(timezone.utc)
    params = {"page": "1", "per_page": "100"}
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = REPO_WORKFLOWS_URL_FMT.format(owner=owner, repo=repo)
    workflows = []
    status_count = {}
    for status in ["queued", "in_progress"]:
        r = requests.get(
            url,
            headers=headers,
            params={**params, **{"status": status}},
        )
        r.raise_for_status()
        workflows.extend(r.json().get("workflow_runs", []))
        status_count[status] = r.json().get("total_count")
        while "next" in r.links.keys():
            r = requests.get(r.links["next"]["url"], headers=headers)
            r.raise_for_status()
            workflows.extend(r.json().get("workflow_runs", []))
    return workflows, status_count, timestamp


# pylint: disable=too-many-locals
def fetch_github_actions_queue(
    owner: str, repos: List[str], csv_file: str, output_dir: str
) -> None:
    print(f"Fetching repos ({len(repos)}) (in_progress, queued):")
    with open(csv_file, mode="w") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for repo in repos:
            workflows, status_count, timestamp = fetch_repo_queue(owner, repo)
            queued = status_count["queued"]
            in_progress = status_count["in_progress"]
            csv_data = {
                "repository_name": repo,
                "repository_owner": owner,
                "queued": in_progress,
                "in_progress": queued,
                "timestamp": timestamp,
            }
            print(f"{owner}/{repo}: {in_progress}, {queued}")
            writer.writerow(csv_data)

            directory = os.path.join(output_dir, owner, repo)
            filename = os.path.join(
                directory, timestamp.strftime("%Y%m%d_%H%M%SZ") + ".json"
            )
            os.makedirs(directory, exist_ok=True)
            with open(filename, "w") as f:
                json.dump(workflows, f)


if __name__ == "__main__":
    input_file, bq_csv_file, out_dir = parse_args()
    repositories_owner, repositories = parse_input_file(input_file)
    fetch_github_actions_queue(repositories_owner, repositories, bq_csv_file, out_dir)
