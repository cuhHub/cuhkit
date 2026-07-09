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
    ProjectType,
    ProjectConfiguration,
    get_project_file_path,
    does_project_exist_at_path,
    Project,
    AddonProject,
    AddonProjectConfiguration
)

from cuhkit.exceptions import (
    ProjectNotFoundException,
    ProjectLoadFailureException
)

# // Main
def test_project_type_values():
    assert ProjectType.ADDON.value == "addon"
    assert ProjectType.MOD.value == "mod"

def test_project_configuration_defaults(temp_dir: Path):
    config = ProjectConfiguration(name = "test", project_type = ProjectType.ADDON, path = temp_dir)

    assert config.name == "test"
    assert config.project_type == ProjectType.ADDON
    assert config.path == temp_dir
    assert config.src == temp_dir / "src"

def test_project_configuration_custom_src(temp_dir: Path):
    custom_src = temp_dir / "custom_src"
    config = ProjectConfiguration(name = "test", project_type = ProjectType.ADDON, path = temp_dir, src = custom_src)

    assert config.src == custom_src

def test_get_project_file_path(temp_dir: Path):
    file_path = get_project_file_path(temp_dir)
    assert file_path == temp_dir / ".cuhkitproj.json"

def test_does_project_exist_at_path_false(temp_dir: Path):
    assert does_project_exist_at_path(temp_dir) is False

def test_does_project_exist_at_path_true(temp_dir: Path):
    project_file = temp_dir / ".cuhkitproj.json"
    project_file.write_text("{}")

    assert does_project_exist_at_path(temp_dir) is True

def test_does_project_exist_at_path_with_file(temp_dir: Path):
    project_file = temp_dir / ".cuhkitproj.json"
    project_file.write_text("{}")

    assert does_project_exist_at_path(project_file) is True

def test_does_project_exist_at_path_with_wrong_file(temp_dir: Path):
    other_file = temp_dir / "other.json"
    other_file.write_text("{}")

    assert does_project_exist_at_path(other_file) is False

def test_project_save_and_delete(temp_dir: Path):
    config = AddonProjectConfiguration(name = "test", path = temp_dir)
    project = AddonProject(config)

    project.save()
    assert (temp_dir / ".cuhkitproj.json").exists()

    project.delete()
    assert not (temp_dir / ".cuhkitproj.json").exists()

def test_project_get_publish_name(temp_dir: Path):
    config = AddonProjectConfiguration(name = "test", path = temp_dir)
    project = AddonProject(config)

    assert project.get_publish_name(False) == "test"
    assert project.get_publish_name(True) == "test_dev"

def test_project_properties(temp_dir: Path):
    config = AddonProjectConfiguration(name = "test", path = temp_dir)
    project = AddonProject(config)

    assert project.name == "test"
    assert project.project_type == ProjectType.ADDON
    assert project.path == temp_dir
    assert project.src == temp_dir / "src"

def test_project_from_path_raises_not_found(temp_dir: Path):
    with pytest.raises(ProjectNotFoundException):
        AddonProject.from_path(temp_dir)

def test_project_from_path_raises_load_failure(temp_dir: Path):
    project_file = temp_dir / ".cuhkitproj.json"
    project_file.write_text("invalid json")

    with pytest.raises(ProjectLoadFailureException):
        AddonProject.from_path(project_file)