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
from __future__ import annotations

import os
from pathlib import Path

from . import (
    Project,
    ProjectConfiguration,
    ProjectType,
    does_project_exist_at_path
)

from cuhkit.exceptions import (
    ProjectAlreadyExistsException
)

from cuhkit.libs import mod_builder
from cuhkit.libs.timeit import TimeIt
from cuhkit.log import logger

# // Main
__all__ = [
    "ModProjectConfiguration",
    "ModProject",
    "create_mod_project"
]

class ModProjectConfiguration(ProjectConfiguration):
    """
    A mod project configuration.
    """

    project_type: ProjectType = ProjectType.MOD
    mod_build_destination: Path = Path(".build/mod.zip")
    stormworks_mods_path: Path = Path(os.environ["APPDATA"]) / "Stormworks" / "data" / "mods"

class ModProject(Project[ModProjectConfiguration]):
    """
    A cuhkit mod project.
    """
    
    def __init__(self, project_configuration: ModProjectConfiguration):
        """
        Initialises cuhkit mod projects.

        Args:
            project_configuration (ModProjectConfiguration): The cuhkit mod project configuration
        """

        super().__init__(
            project_configuration = project_configuration
        )

    @staticmethod
    def get_project_configuration_from_content(content: str) -> ModProjectConfiguration:
        """
        Returns a project configuration instance from the content of a project file.

        Args:
            content (str): The content of the cuhkit project file.
            
        Returns:
            ModProjectConfiguration: The project configuration.
        """

        return ModProjectConfiguration.model_validate_json(content)

def create_mod_project(name: str, path: Path) -> ModProject:
    """
    Creates a cuhkit mod project.

    Args:
        name (str): The name of the mod project.
        path (Path): The path to the directory to create the mod project in.
        
    Raises:
        ValueError: If the path is not a directory.
        ProjectAlreadyExistsException: If a cuhkit project already exists at the path.

    Returns:
        ModProject: The created cuhkit mod project.
    """

    if not path.is_dir():
        raise ValueError(f"Path must be a directory: {path}")
    
    if does_project_exist_at_path(path):
        raise ProjectAlreadyExistsException(f"A cuhkit project already exists at path: {path}")
    
    return ModProject(
        project_configuration = ModProjectConfiguration(
            name = name,
            path = path
        )
    )