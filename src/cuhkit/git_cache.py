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
from pydantic import BaseModel
from pathlib import Path
from hashlib import sha1
import shutil
import os
import stat
from datetime import datetime, timezone
from typing import Optional

from cuhkit import CUHKIT_DATA_PATH
from cuhkit.log import logger

# // Main
GIT_CACHE_PATH = CUHKIT_DATA_PATH / "git_cache.json"
GIT_CACHE_REPOS_PATH = CUHKIT_DATA_PATH / "git_cache_repos"

_fetched_repos: set[tuple[str, str]] = set()

class GitCacheEntry(BaseModel):
    """
    Represents a single cached git repo entry.
    """

    repo_url: str
    branch: str
    cloned_path: Path
    last_used: str

class GitCache(BaseModel):
    """
    Manages cached git repos with persistent metadata.
    """

    path: Path
    entries: list[GitCacheEntry] = []

    def _get_entry(self, repo_url: str, branch: str) -> Optional[GitCacheEntry]:
        """
        Gets a cached entry by repo URL and branch.

        Args:
            repo_url (str): The URL of the git repo.
            branch (str): The branch to use.

        Returns:
            Optional[GitCacheEntry]: The cached entry, or None if not found.
        """

        for entry in self.entries:
            if entry.repo_url == repo_url and entry.branch == branch:
                return entry

        return None

    def has_entry(self, repo_url: str, branch: str) -> bool:
        """
        Checks if a cached entry exists for the given repo URL and branch.

        Args:
            repo_url (str): The URL of the git repo.
            branch (str): The branch to use.

        Returns:
            bool: Whether the entry exists.
        """

        return self._get_entry(repo_url, branch) is not None

    def get_entry(self, repo_url: str, branch: str) -> Optional[GitCacheEntry]:
        """
        Gets a cached entry by repo URL and branch, updating its last_used timestamp.

        Args:
            repo_url (str): The URL of the git repo.
            branch (str): The branch to use.

        Returns:
            Optional[GitCacheEntry]: The cached entry, or None if not found.
        """

        entry = self._get_entry(repo_url, branch)

        if entry is not None:
            entry.last_used = datetime.now(timezone.utc).isoformat()
            self.save()

        return entry

    def add_entry(self, repo_url: str, branch: str, cloned_path: Path):
        """
        Adds a new entry to the cache.

        Args:
            repo_url (str): The URL of the git repo.
            branch (str): The branch to use.
            cloned_path (Path): The path where the repo is cloned.
        """

        entry = GitCacheEntry(
            repo_url = repo_url,
            branch = branch,
            cloned_path = cloned_path,
            last_used = datetime.now(timezone.utc).isoformat()
        )

        self.entries.append(entry)
        self.save()

        logger.debug(f"git_cache: Added entry for {repo_url} (branch: {branch})")

    def save(self):
        """
        Saves the cache to disk.
        """

        logger.debug(f"git_cache: Saving cache to {self.path}")
        self.path.write_text(self.model_dump_json(indent = 3))

    def clear(self):
        """
        Clears all cached repos and removes their cloned directories.
        """

        logger.info(f"git_cache: Clearing all cached repos...")

        for entry in self.entries:
            if entry.cloned_path.exists():
                logger.debug(f"git_cache: Removing cloned repo at {entry.cloned_path}")
                shutil.rmtree(entry.cloned_path, onexc = _handle_rmtree_error)

        self.entries.clear()
        self.save()

        logger.info(f"git_cache: Cache cleared.")

    @classmethod
    def create_new(cls, path: Path):
        """
        Creates a new cache, saving it automatically.

        Args:
            path (Path): The path to the cache file.
        """

        cache = cls(path = path)
        cache.save()

        return cache

    @classmethod
    def try_load(cls, path: Path) -> "GitCache":
        """
        Loads the cache from the file, or creates a new one if it doesn't exist.

        Args:
            path (Path): The path to the cache file.

        Returns:
            GitCache: The loaded cache.
        """

        if not path.exists():
            logger.debug(f"git_cache: No cache found at {path}. Creating new.")
            return cls.create_new(path)

        logger.debug(f"git_cache: Loading cache from: {path}")

        content = path.read_text()
        return cls.model_validate_json(content)

def _handle_rmtree_error(function: callable, path: str, excinfo: Exception):
    """
    Handles errors during shutil.rmtree, specifically for Windows read-only file issues.

    Args:
        function (callable): The function that raised the error.
        path (str): The path of the file/directory that caused the error.
        excinfo (Exception): The exception information.
    """

    if isinstance(excinfo, PermissionError):
        logger.debug(f"git_cache: Removing read-only attribute from {path}")
        os.chmod(path, stat.S_IWRITE)
        function(path)
    else:
        raise excinfo

def get_repo_hash(repo_url: str, branch: str) -> str:
    """
    Generates a hash for a given repo URL and branch.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.

    Returns:
        str: A hash representing the repo and branch.
    """

    return sha1(f"{repo_url}:{branch}".encode()).hexdigest()

def get_cloned_path(repo_url: str, branch: str) -> Path:
    """
    Returns the expected cloned path for a given repo URL and branch.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.

    Returns:
        Path: The path where the repo would be cloned.
    """

    return GIT_CACHE_REPOS_PATH / get_repo_hash(repo_url, branch)

def get_cache() -> GitCache:
    """
    Loads the git cache from the metadata file.

    Returns:
        GitCache: The loaded cache.
    """

    GIT_CACHE_PATH.parent.mkdir(parents = True, exist_ok = True)
    GIT_CACHE_REPOS_PATH.mkdir(parents = True, exist_ok = True)

    return GitCache.try_load(GIT_CACHE_PATH)

def was_fetched(repo_url: str, branch: str) -> bool:
    """
    Checks if a repo has been fetched in the current runtime.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.

    Returns:
        bool: Whether the repo has been fetched this runtime.
    """

    return (repo_url, branch) in _fetched_repos

def mark_fetched(repo_url: str, branch: str):
    """
    Marks a repo as fetched for the current runtime.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.
    """

    _fetched_repos.add((repo_url, branch))
    logger.debug(f"git_cache: Marked {repo_url} (branch: {branch}) as fetched for this runtime")

def clear_cache():
    """
    Clears the git cache.
    """

    cache = get_cache()
    cache.clear()

cache = get_cache()