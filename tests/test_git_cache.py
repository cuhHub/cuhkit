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
from pathlib import Path

from cuhkit.git_cache import (
    GitCache,
    GitCacheEntry,
    get_cloned_path,
    get_repo_hash,
    was_fetched,
    mark_fetched,
    clear_cache
)

# // Main
def test_git_cache_creation(empty_git_cache: GitCache):
    assert empty_git_cache.path.exists()
    assert len(empty_git_cache.entries) == 0

def test_git_cache_add_entry(empty_git_cache: GitCache):
    cloned_path = Path("/tmp/test_repo")

    empty_git_cache.add_entry("https://github.com/user/repo.git", "main", cloned_path)

    assert len(empty_git_cache.entries) == 1
    assert empty_git_cache.entries[0].repo_url == "https://github.com/user/repo.git"
    assert empty_git_cache.entries[0].branch == "main"
    assert empty_git_cache.entries[0].cloned_path == cloned_path

def test_git_cache_has_entry(empty_git_cache: GitCache):
    empty_git_cache.add_entry("https://github.com/user/repo.git", "main", Path("/tmp/repo"))

    assert empty_git_cache.has_entry("https://github.com/user/repo.git", "main") is True
    assert empty_git_cache.has_entry("https://github.com/user/repo.git", "dev") is False
    assert empty_git_cache.has_entry("https://github.com/other/repo.git", "main") is False

def test_git_cache_get_entry(empty_git_cache: GitCache):
    cloned_path = Path("/tmp/repo")
    empty_git_cache.add_entry("https://github.com/user/repo.git", "main", cloned_path)

    entry = empty_git_cache.get_entry("https://github.com/user/repo.git", "main")
    assert entry is not None
    assert entry.cloned_path == cloned_path

def test_git_cache_get_entry_nonexistent(empty_git_cache: GitCache):
    entry = empty_git_cache.get_entry("https://github.com/user/repo.git", "main")
    assert entry is None

def test_git_cache_try_load_creates(temp_git_cache_path: Path):
    assert not temp_git_cache_path.exists()

    cache = GitCache.try_load(temp_git_cache_path)
    assert cache.path == temp_git_cache_path
    assert len(cache.entries) == 0

def test_git_cache_try_load_existing(empty_git_cache: GitCache):
    empty_git_cache.add_entry("https://github.com/user/repo.git", "main", Path("/tmp/repo"))

    loaded = GitCache.try_load(empty_git_cache.path)
    assert len(loaded.entries) == 1

def test_git_cache_clear(empty_git_cache: GitCache):
    empty_git_cache.add_entry("https://github.com/user/repo.git", "main", Path("/tmp/repo"))
    assert len(empty_git_cache.entries) == 1

    empty_git_cache.clear()
    assert len(empty_git_cache.entries) == 0

def test_get_repo_hash():
    hash1 = get_repo_hash("https://github.com/user/repo.git", "main")
    hash2 = get_repo_hash("https://github.com/user/repo.git", "main")
    hash3 = get_repo_hash("https://github.com/other/repo.git", "main")

    assert hash1 == hash2
    assert hash1 != hash3

def test_get_cloned_path():
    repo_url = "https://github.com/user/repo.git"
    branch = "main"

    path = get_cloned_path(repo_url, branch)
    assert isinstance(path, Path)
    assert path.name == get_repo_hash(repo_url, branch)

def test_was_fetched_and_mark_fetched():
    repo_url = "https://github.com/user/repo.git"
    branch = "main"

    assert was_fetched(repo_url, branch) is False

    mark_fetched(repo_url, branch)
    assert was_fetched(repo_url, branch) is True

def test_was_fetched_different_branches():
    mark_fetched("https://github.com/user/repo.git", "main")

    assert was_fetched("https://github.com/user/repo.git", "main") is True
    assert was_fetched("https://github.com/user/repo.git", "dev") is False

def test_git_cache_persists_entries(empty_git_cache: GitCache):
    empty_git_cache.add_entry("https://github.com/user/repo.git", "main", Path("/tmp/repo"))
    empty_git_cache.save()

    loaded = GitCache.try_load(empty_git_cache.path)
    assert len(loaded.entries) == 1
    assert loaded.entries[0].repo_url == "https://github.com/user/repo.git"