#!/usr/bin/env python
import logging
import subprocess
from argparse import ArgumentParser
from multiprocessing import Pool
from os import environ, path

import requests


logging.basicConfig(level=logging.INFO)


def update_repo(repository):
    target = repository["owner"]["login"]
    repository_name = repository["name"]
    clone_path = path.join("out", target, repository_name)
    clone_command = ("git", "clone", repository["ssh_url"], clone_path)
    logging.info("Running %s", clone_command)
    process = subprocess.run(clone_command)
    if process.returncode:
        fetch_command = ("git", "fetch")
        logging.info("Running %s in %s", fetch_command, clone_path)
        subprocess.run(fetch_command, cwd=clone_path, check=True)


def main():
    url = (
        "https://api.github.com/{type}/{clone_target}/repos?"
        "access_token={token}&per_page=200"
    ).format(
        type=args.type,
        clone_target=args.target,
        token=environ["ACCESS_TOKEN"],
    )
    repositories = requests.get(url).json()
    logging.info("Cloning %d repositories", len(url))

    with Pool() as pool:
        pool.map(update_repo, repositories)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('target')
    parser.add_argument('--type', choices=["users", "orgs"], default="users")
    args = parser.parse_args()
    main()
