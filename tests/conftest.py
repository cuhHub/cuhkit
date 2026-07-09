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
from uuid import uuid4

from pathlib import Path

from cuhkit.git_cache import GitCache
from cuhkit.credentials import Credentials

# // Main
@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    return tmp_path

@pytest.fixture
def temp_credentials_path(temp_dir: Path) -> Path:
    return temp_dir / "credentials.json"

@pytest.fixture
def temp_git_cache_path(temp_dir: Path) -> Path:
    return temp_dir / "git_cache.json"

@pytest.fixture
def empty_credentials(temp_credentials_path: Path) -> Credentials:
    return Credentials(path = temp_credentials_path)

@pytest.fixture
def saved_credentials(temp_credentials_path: Path) -> Credentials:
    credentials = Credentials(path = temp_credentials_path)
    credentials.save()

    return credentials

@pytest.fixture
def credentials_with_token(temp_credentials_path: Path) -> Credentials:
    credentials = Credentials(api_token = uuid4(), path = temp_credentials_path)
    credentials.save()

    return credentials

@pytest.fixture
def empty_git_cache(temp_git_cache_path: Path) -> GitCache:
    return GitCache.create_new(temp_git_cache_path)

@pytest.fixture
def sample_addon_src(temp_dir: Path) -> Path:
    src_dir = temp_dir / "src"
    src_dir.mkdir(parents = True, exist_ok = True)

    (src_dir / "main.lua").write_text('print("hello world")')
    (src_dir / "lib.lua").write_text('local lib = {}')

    return src_dir