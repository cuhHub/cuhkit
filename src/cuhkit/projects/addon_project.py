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

from cuhkit.libs import addon_builder

# // Main
__all__ = [
    "AddonProjectConfiguration",
    "AddonProject",
    "create_addon_project"
]

class AddonProjectConfiguration(ProjectConfiguration):
    """
    An addon project configuration.
    """

    project_type: ProjectType = ProjectType.ADDON
    build_destination: Path = Path(".build/addon.lua")
    stormworks_addon_directory: Path = Path(os.environ["APPDATA"]) / "Stormworks" / "data" / "missions"

class AddonProject(Project):
    """
    A cuhkit addon project.
    """
    
    def __init__(self, name: str, path: Path):
        """
        Initialises cuhkit addon projects.

        Args:
            name (str): The name of the addon project.
            path (Path): The path to the addon project.
        """

        super().__init__(
            name = name,
            project_type = ProjectType.ADDON,
            path = path
        )
        
        self.project_configuration = self.get_project_configuration()
        
    def build(self):
        """
        Builds the addon project.
        """

        addon_builder.build_addon(self.path, self.project_configuration.build_destination)
        
    def get_project_configuration(self) -> AddonProjectConfiguration:
        """
        Returns the project configuration.

        Returns:
            AddonProjectConfiguration: The project configuration.
        """

        return AddonProjectConfiguration(
            name = self.name,
            path = self.path
        )
        
    @staticmethod
    def get_project_configuration_from_content(content: str) -> AddonProjectConfiguration:
        """
        Returns a project configuration instance from the content of a project file.

        Args:
            content (str): The content of the project file.
            
        Returns:
            AddonProjectConfiguration: The project configuration.
        """

        return AddonProjectConfiguration.model_validate_json(content)
    
    @classmethod
    def from_project_configuration(cls, project_configuration: AddonProjectConfiguration) -> AddonProject:
        """
        Creates an addon project from a project configuration.

        Args:
            project_configuration (AddonProjectConfiguration): The project configuration to create the cuhkit addon project from.
                
        Returns:
            AddonProject: The created cuhkit addon project.
        """
        
        return cls(
            name = project_configuration.name,
            path = project_configuration.path
        )

def create_addon_project(name: str, path: Path) -> AddonProject:
    """
    Creates a cuhkit addon project.

    Args:
        name (str): The name of the addon project.
        path (Path): The path to the directory to create the addon project in.
    
    Raises:
        ValueError: If the path is not a directory.
        ProjectAlreadyExistsException: If a cuhkit project already exists at the path.

    Returns:
        AddonProject: The created cuhkit addon project.
    """

    if not path.is_dir():
        raise ValueError(f"Path must be a directory: {path}")
    
    if does_project_exist_at_path(path):
        raise ProjectAlreadyExistsException(f"A cuhkit project already exists at path: {path}")
    
    return AddonProject(
        name = name,
        path = path
    )