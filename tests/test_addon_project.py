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
from unittest.mock import patch, MagicMock

from cuhkit.projects import (
    AddonProject,
    AddonProjectConfiguration,
    create_addon_project,
    ProjectType
)

from cuhkit.exceptions import ProjectAlreadyExistsException

# // Main
def test_addon_project_configuration_defaults():
    config = AddonProjectConfiguration(name = "test", path = Path("/tmp"))

    assert config.project_type == ProjectType.ADDON
    assert config.build_destination == Path(".build/addon.lua")
    assert config.stormworks_addons_path is None

def test_create_addon_project(temp_dir: Path):
    project = create_addon_project("test_addon", temp_dir)

    assert project.name == "test_addon"
    assert project.project_type == ProjectType.ADDON
    assert project.path == temp_dir

def test_create_addon_project_raises_if_not_directory(temp_dir: Path):
    file_path = temp_dir / "file.txt"
    file_path.write_text("")

    with pytest.raises(ValueError):
        create_addon_project("test", file_path)

def test_create_addon_project_raises_if_exists(temp_dir: Path):
    project = create_addon_project("test", temp_dir)
    project.save()

    with pytest.raises(ProjectAlreadyExistsException):
        create_addon_project("test2", temp_dir)

def test_addon_project_configuration_from_content():
    content = '{"name": "test", "project_type": "addon", "path": "/tmp"}'
    config = AddonProject.get_project_configuration_from_content(content)

    assert config.name == "test"
    assert config.project_type == ProjectType.ADDON

def test_addon_project_get_publish_name(temp_dir: Path):
    config = AddonProjectConfiguration(name = "test", path = temp_dir)
    project = AddonProject(config)

    assert project.get_publish_name(False) == "test"
    assert project.get_publish_name(True) == "test_dev"

def test_addon_project_build(temp_dir: Path):
    config = AddonProjectConfiguration(name = "test", path = temp_dir)
    project = AddonProject(config)

    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "main.lua").write_text("-- main")

    with patch("cuhkit.projects.addon_project.addon_builder.build_addon") as mock_build:
        project.build()
        mock_build.assert_called_once()

def test_addon_project_first_time_setup(temp_dir: Path):
    config = AddonProjectConfiguration(name = "test", path = temp_dir)
    project = AddonProject(config)

    with patch("cuhkit.projects.addon_project.templates.copy_template") as mock_copy:
        project.first_time_setup()
        mock_copy.assert_called_once()

def test_addon_project_save(temp_dir: Path):
    project = create_addon_project("test", temp_dir)
    project.save()

    assert (temp_dir / ".cuhkitproj.json").exists()