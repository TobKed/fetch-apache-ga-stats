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

    GITHUB_TOKEN=123 python scripts/fetch_apache_projects_with_ga.py \
        --org apache \
        --output matrix.json

"""
import argparse
import datetime
import json
import logging
import os
from typing import Dict, List, Optional, Tuple

import requests


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--org", help="GitHub Organisation", required=True)
    parser.add_argument("--output", help="Output file", required=True)
    args = parser.parse_args()
    org = args.org
    output_file = args.output
    return org, output_file


LOGGING_LEVEL: int = (
    logging.DEBUG if os.getenv("ACTIONS_RUNNER_DEBUG") else logging.INFO
)
GITHUB_TOKEN: str = os.environ["GITHUB_TOKEN"]
ORG, OUTPUT_FILE = parse_args()
ORG_REPOS_QUERY_URL_FMT: str = "https://api.github.com/orgs/{org}/repos"
REPO_WORKFLOWS_URL_FMT: str = "https://api.github.com/repos/{org}/{repo}/actions/runs"
HEADERS: Dict[str, str] = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}


class QuotaException(Exception):
    def __init__(
        self,
        request: requests.Response,
        repo: Optional[str] = None,
    ) -> None:
        logging.error(f"Repo: {repo}")
        logging.error(f"request.text: {getattr(request, 'text', '')}")
        logging.error(f"request.content: {getattr(request, 'content', '')}")

        headers = getattr(request, "headers", {})
        rate_limit_reset = headers.get("X-RateLimit-Reset")
        data = {
            "X-RateLimit": headers.get("X-RateLimit"),
            "X-RateLimit-Remaining": headers.get("X-RateLimit-Remaining"),
            "X-RateLimit-Reset": rate_limit_reset,
        }
        logging.error(f"PossibleQuotaException:\n{data}")
        if rate_limit_reset:
            logging.error(
                f"Limit will reset at: "
                f"{datetime.datetime.fromtimestamp(int(rate_limit_reset)).isoformat()}"
            )


def raise_for_status(request: requests.Response):
    rate_limit_remianing: int = int(request.headers.get("X-RateLimit-Remaining", 1))
    if rate_limit_remianing == 0:
        raise QuotaException(request)
    try:
        request.raise_for_status()
    except:  # noqa
        logging.error(f"request.text: {getattr(request, 'text', '')}")
        logging.error(f"request.content: {getattr(request, 'content', '')}")
        raise


def get_org_repos_names(org: str) -> List[str]:
    print(f"### Start fetching '{org}' repos names ###")
    params = {"page": 1, "per_page": 100}
    r = requests.get(
        ORG_REPOS_QUERY_URL_FMT.format(org=org), headers=HEADERS, params=params
    )
    raise_for_status(r)
    _repos = [d["name"] for d in r.json()]

    while "next" in r.links.keys():
        print("|", end="")
        r = requests.get(r.links["next"]["url"], headers=HEADERS)
        raise_for_status(r)
        _repos.extend([d["name"] for d in r.json()])

    print(f"### Finished fetching '{org}' repos names ({len(_repos)}) ###")
    return _repos


def check_which_org_repos_use_ga(
    organisation: str, repositories: List[str]
) -> List[str]:
    print(f"### Start checking which of {len(repositories)} repos use GA ###")
    repositories: Tuple[str] = tuple(set(repositories))  # type: ignore
    counter: int = 0
    _repos_with_ga: List[str] = []

    for repo in repositories:
        counter += 1
        logging.debug(counter)
        url: str = REPO_WORKFLOWS_URL_FMT.format(org=organisation, repo=repo)
        r = requests.get(url, headers=HEADERS)
        raise_for_status(r)
        if r.json().get("total_count"):
            logging.debug(f" '{organisation}/{repo}' using GA: true")
            _repos_with_ga.append(repo)

    print(
        f"### Finished checking which repos use GA "
        f"({len(_repos_with_ga)}/{len(repos)}) ###"
    )
    return _repos_with_ga


def save_json_file(organisation: str, repositories: List[str], file: str) -> None:
    repositories.sort()
    data = {"organisation": [organisation], "repository": repositories}
    with open(file, "w") as outfile:
        json.dump(data, outfile, indent=4)


if __name__ == "__main__":
    logging.basicConfig(level=LOGGING_LEVEL)
    repos = get_org_repos_names(org=ORG)
    repos_with_ga = check_which_org_repos_use_ga(organisation=ORG, repositories=repos)
    save_json_file(organisation=ORG, repositories=repos_with_ga, file=OUTPUT_FILE)
