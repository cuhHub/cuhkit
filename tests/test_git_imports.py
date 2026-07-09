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
import pytest
from unittest.mock import patch, MagicMock

from pathlib import Path

from cuhkit.libs.git_imports import import_paths_in_repo, _import_paths_from_repo

# // Main
@pytest.fixture
def mock_repo_cls():
    with patch("cuhkit.libs.git_imports.Repo") as mock_repo_class:
        mock_instance = MagicMock()
        mock_repo_class.clone_from.return_value = mock_instance

        yield mock_repo_class, mock_instance

@pytest.fixture
def mock_cache(mock_repo_cls):
    with patch("cuhkit.libs.git_imports.cache") as mock_cache:
        mock_cache.get_entry.return_value = None
        mock_cache.add_entry = MagicMock()

        yield mock_cache

def test_import_paths_clones_when_no_cache(mock_cache, mock_repo_cls, temp_dir: Path):
    mock_cache.get_entry.return_value = None

    cloned_path = temp_dir / "cloned"
    cloned_path.mkdir(parents = True, exist_ok = True)
    (cloned_path / "libs").mkdir()
    (cloned_path / "libs" / "mylib.lua").write_text("-- lib")

    with patch("cuhkit.libs.git_imports.get_cloned_path", return_value = cloned_path):
        with patch("cuhkit.libs.git_imports.was_fetched", return_value = True):
            with patch("cuhkit.libs.git_imports.mark_fetched") as mock_mark:
                import_paths_in_repo("https://github.com/user/repo.git", "main", [Path("libs")], temp_dir / "output")

    repo_class, instance = mock_repo_cls
    repo_class.clone_from.assert_called_once()
    mock_cache.add_entry.assert_called_once()

def test_import_paths_uses_cached_repo(mock_cache, mock_repo_cls, temp_dir: Path):
    cloned_path = temp_dir / "cached_repo"
    cloned_path.mkdir(parents = True, exist_ok = True)
    (cloned_path / "libs").mkdir()
    (cloned_path / "libs" / "mylib.lua").write_text("-- lib")

    mock_cache.get_entry.return_value = MagicMock(cloned_path = cloned_path)

    with patch("cuhkit.libs.git_imports.was_fetched", return_value = True):
        import_paths_in_repo("https://github.com/user/repo.git", "main", [Path("libs")], temp_dir / "output")

    repo_class, instance = mock_repo_cls
    repo_class.clone_from.assert_not_called()
    mock_cache.add_entry.assert_not_called()