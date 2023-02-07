#!/usr/bin/env python
import subprocess
from argparse import ArgumentParser
from multiprocessing import Pool
from os import environ
from pathlib import Path

import requests


out_folder = Path("out")


def update_repo(repository):
    target = repository["owner"]["login"]
    repository_name = repository["name"]
    print("Cloning" ,repository_name)
    clone_path = out_folder / target / repository_name
    clone_command = ("git", "clone", repository["ssh_url"], clone_path)
    print("Running", clone_command)
    process = subprocess.run(clone_command)
    if process.returncode:
        fetch_command = ("git", "fetch")
        print("Running", fetch_command, "in", clone_path)
        subprocess.run(fetch_command, cwd=clone_path, check=True)


def main():
    access_token = environ["ACCESS_TOKEN"]
    url = (
        f"https://api.github.com/{args.type}/{args.target}/repos?per_page=200"
    )
    session = requests.Session()
    session.headers.update({"Authorization": access_token})
    print("Requesting", url)
    repositories = session.get(url).json()
    print(f"Cloning or fetching {len(url)} repositories")

    with Pool() as pool:
        pool.map(update_repo, repositories)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('--type', choices=["users", "orgs"], default="users")
    args = parser.parse_args()
    main()
