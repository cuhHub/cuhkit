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
from pathlib import Path

from cuhkit.projects import (
    load_project_at_path,
    create_addon_project,
    create_mod_project,
    does_project_exist_at_path
)

from cuhkit.exceptions import (
    ProjectNotFoundException,
    ProjectLoadFailureException
)

# // Main
def test_load_addon_project(temp_dir: Path):
    project = create_addon_project("test_addon", temp_dir)
    project.save()

    loaded = load_project_at_path(temp_dir)
    assert loaded.name == "test_addon"
    assert loaded.project_type.value == "addon"

def test_load_mod_project(temp_dir: Path):
    project = create_mod_project("test_mod", temp_dir)
    project.save()

    loaded = load_project_at_path(temp_dir)
    assert loaded.name == "test_mod"
    assert loaded.project_type.value == "mod"

def test_load_project_raises_not_found(temp_dir: Path):
    with pytest.raises(ProjectNotFoundException):
        load_project_at_path(temp_dir)

def test_load_project_raises_on_invalid_json(temp_dir: Path):
    project_file = temp_dir / ".cuhkitproj.json"
    project_file.write_text("not valid json")

    with pytest.raises(ProjectLoadFailureException):
        load_project_at_path(temp_dir)

def test_load_project_raises_on_invalid_project_type(temp_dir: Path):
    project_file = temp_dir / ".cuhkitproj.json"
    project_file.write_text('{"project_type": "invalid_type"}')

    with pytest.raises(ProjectLoadFailureException):
        load_project_at_path(temp_dir)

def test_does_project_exist_at_path_after_creation(temp_dir: Path):
    assert does_project_exist_at_path(temp_dir) is False

    create_addon_project("test", temp_dir).save()
    assert does_project_exist_at_path(temp_dir) is True