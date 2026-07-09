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

from cuhkit.credentials import Credentials

# // Main
def test_credentials_creation(empty_credentials: Credentials):
    assert empty_credentials.api_token is None
    assert empty_credentials.path is not None

def test_credentials_save(empty_credentials: Credentials):
    empty_credentials.save()

    assert empty_credentials.path.exists()

    content = empty_credentials.path.read_text()
    assert "api_token" in content

def test_credentials_save_with_token(credentials_with_token: Credentials):
    assert credentials_with_token.path.exists()

    loaded = Credentials.model_validate_json(credentials_with_token.path.read_text())
    assert loaded.api_token == credentials_with_token.api_token

def test_credentials_remove(saved_credentials: Credentials):
    assert saved_credentials.path.exists()

    saved_credentials.remove()
    assert not saved_credentials.path.exists()

def test_credentials_create_new(temp_credentials_path: Path):
    credentials = Credentials.create_new(temp_credentials_path)

    assert credentials.path.exists()
    assert credentials.api_token is None

def test_credentials_try_load_creates_if_not_exists(temp_credentials_path: Path):
    assert not temp_credentials_path.exists()

    credentials = Credentials.try_load(temp_credentials_path)
    assert credentials.path.exists()
    assert credentials.api_token is None

def test_credentials_try_load_existing(credentials_with_token: Credentials):
    loaded = Credentials.try_load(credentials_with_token.path)

    assert loaded.api_token == credentials_with_token.api_token

def test_credentials_round_trip(temp_credentials_path: Path):
    original = Credentials(api_token = uuid4(), path = temp_credentials_path)
    original.save()

    loaded = Credentials.try_load(temp_credentials_path)
    assert loaded.api_token == original.api_token

def test_credentials_remove_nonexistent(temp_credentials_path: Path):
    credentials = Credentials(path = temp_credentials_path)

    with pytest.raises(FileNotFoundError):
        credentials.remove()