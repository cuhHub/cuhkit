"""
----------------------------------------------
cuhkit - A CLI-oriented Python package for handling cuhHub Stormworks projects (addons/mods).
https://github.com/cuhHub/cuhkit
----------------------------------------------

Copyright (C) 2026 cuhHub

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

# // Imports
from git import Repo
from pathlib import Path
import shutil

from cuhkit.log import logger

from cuhkit.git_cache import (
    cache,
    get_cloned_path,
    was_fetched,
    mark_fetched
)

# // Main
def import_path_in_repo(repo_url: str, branch: str, path: Path, destination: Path):
    """
    Imports a folder/file from a git repo.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.
        path (Path): The path of the file/folder in the repo
        destination (Path): The path to import the file/folder to.

    Raises:
        FileNotFoundError: If the path does not exist in the repo.
    """

    _import_path_from_repo(repo_url, branch, path, destination)

def _import_path_from_repo(repo_url: str, branch: str, path: Path, destination: Path):
    """
    Internal function to import a path from an already-cloned or newly-cloned repo.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.
        path (Path): The path of the file/folder in the repo
        destination (Path): The path to import the file/folder to.

    Raises:
        FileNotFoundError: If the path does not exist in the repo.
        ValueError: If `path` is a directory while `destination` is a file.
    """

    entry = cache.get_entry(repo_url, branch)

    if entry is None:
        cloned_repo_path = get_cloned_path(repo_url, branch)

        logger.debug(f"git_import: Cloning repo ({repo_url}, branch: {branch}) to cache: {cloned_repo_path}")

        repo = Repo.clone_from(
            repo_url,
            str(cloned_repo_path),
            depth = 1,
            no_checkout = True,
            filter = "blob:none",
            branch = branch
        )

        repo.git.sparse_checkout("init", "--cone")
        repo.git.checkout("HEAD")

        cache.add_entry(repo_url, branch, cloned_repo_path)
        mark_fetched(repo_url, branch)
    else:
        cloned_repo_path = entry.cloned_path

        if not was_fetched(repo_url, branch):
            logger.debug(f"git_import: Fetching latest for cached repo at {cloned_repo_path}")

            repo = Repo(str(cloned_repo_path))
            repo.remotes.origin.fetch(depth = 1)
            repo.git.checkout(branch)
            repo.git.reset("--hard", f"origin/{branch}")

            mark_fetched(repo_url, branch)
        else:
            logger.debug(f"git_import: Using cached repo at {cloned_repo_path} (already fetched this runtime)")

    repo = Repo(str(cloned_repo_path))
    repo.git.sparse_checkout("set", str(path))

    src = cloned_repo_path / path

    if not src.exists():
        raise FileNotFoundError(f"Path does not exist in repo: {src}")

    if src.is_dir():
        if destination.suffix:
            raise ValueError("Cannot import a directory to a file.")

        destination.mkdir(parents = True, exist_ok = True)

        logger.debug(f"git_import: Copying directory {src} to {destination}")
        shutil.copytree(src, destination, dirs_exist_ok = True)

    else:
        if destination.suffix:
            logger.debug(f"git_import: Copying file {src} to {destination}")
            shutil.copy2(src, destination)
        else:
            logger.debug(f"git_import: Copying file {src} to directory {destination}")
            destination.mkdir(parents = True, exist_ok = True)
            shutil.copy2(src, destination / src.name)