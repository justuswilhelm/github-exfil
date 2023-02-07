#!/usr/bin/env python
from itertools import count
import subprocess
from argparse import ArgumentParser
from multiprocessing import Pool
from os import environ
from pathlib import Path

import requests


API_BASE = "https://api.github.com/"
out_folder = Path("out")


def update_repo(repository):
    target = repository["owner"]["login"]
    repository_name = repository["name"]
    print(f"Attempting to clone {repository_name}")
    clone_path = out_folder / target / repository_name
    clone_command = ("git", "clone", repository["ssh_url"], clone_path)
    print(f"Running f{clone_command}")
    process = subprocess.run(clone_command)
    if process.returncode:
        print(f"Not successful with status {process.returncode}")
        print("Assuming already cloned and needing to pull")
        pull_command = ("git", "pull")
        print(f"Running {pull_command} in {clone_path}")
        subprocess.run(pull_command, cwd=clone_path, check=True)
        lfs_command = "git", "lfs", "pull"
        print(f"Running {lfs_command}")
        subprocess.run(lfs_command, cwd=clone_path, check=True)


def main():
    access_token = environ["ACCESS_TOKEN"]
    if args.type == "self":
        url = f"{API_BASE}user/repos"
    else:
        url = (
            f"{API_BASE}{args.type}/{args.target}/repos"
        )
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {access_token}"})

    repositories = []
    for page in count(1):
        print(f"Retrieving page # {page}")
        page_url = f"{url}?per_page=100&page={page}"
        print(f"Requesting {page_url}")
        result = session.get(page_url).json()
        print(f"Got {len(result)} repositories")
        repositories.extend(result)
        if len(result) < 100:
            break

    print(f"Cloning or pulling {len(repositories)} repositories")
    with Pool() as pool:
        pool.map(update_repo, repositories)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('--type', choices=["self", "users", "orgs"], default="users")
    args = parser.parse_args()
    main()
