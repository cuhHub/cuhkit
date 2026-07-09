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
    ModProject,
    ModProjectConfiguration,
    create_mod_project,
    ProjectType
)

from cuhkit.exceptions import ProjectAlreadyExistsException

# // Main
def test_mod_project_configuration_defaults():
    config = ModProjectConfiguration(name = "test", path = Path("/tmp"))

    assert config.project_type == ProjectType.MOD
    assert config.mod_build_destination == Path(".build/mod.zip")
    assert config.stormworks_mods_path is None

def test_create_mod_project(temp_dir: Path):
    project = create_mod_project("test_mod", temp_dir)

    assert project.name == "test_mod"
    assert project.project_type == ProjectType.MOD
    assert project.path == temp_dir

def test_create_mod_project_raises_if_not_directory(temp_dir: Path):
    file_path = temp_dir / "file.txt"
    file_path.write_text("")

    with pytest.raises(ValueError):
        create_mod_project("test", file_path)

def test_create_mod_project_raises_if_exists(temp_dir: Path):
    project = create_mod_project("test", temp_dir)
    project.save()

    with pytest.raises(ProjectAlreadyExistsException):
        create_mod_project("test2", temp_dir)

def test_mod_project_configuration_from_content():
    content = '{"name": "test", "project_type": "mod", "path": "/tmp"}'
    config = ModProject.get_project_configuration_from_content(content)

    assert config.name == "test"
    assert config.project_type == ProjectType.MOD

def test_mod_project_get_publish_name(temp_dir: Path):
    config = ModProjectConfiguration(name = "test", path = temp_dir)
    project = ModProject(config)

    assert project.get_publish_name(False) == "test"
    assert project.get_publish_name(True) == "test_dev"

def test_mod_project_build(temp_dir: Path):
    config = ModProjectConfiguration(name = "test", path = temp_dir)
    project = ModProject(config)

    (temp_dir / "src").mkdir()
    (temp_dir / "src" / "mod.xml").write_text("<mod></mod>")

    with patch("cuhkit.projects.mod_project.mod_builder.build_mod") as mock_build:
        project.build()
        mock_build.assert_called_once()

def test_mod_project_first_time_setup(temp_dir: Path):
    config = ModProjectConfiguration(name = "test", path = temp_dir)
    project = ModProject(config)

    with patch("cuhkit.projects.mod_project.templates.copy_template") as mock_copy:
        project.first_time_setup()
        mock_copy.assert_called_once()

def test_mod_project_save(temp_dir: Path):
    project = create_mod_project("test", temp_dir)
    project.save()

    assert (temp_dir / ".cuhkitproj.json").exists()