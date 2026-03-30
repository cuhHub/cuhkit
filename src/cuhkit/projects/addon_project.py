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

from . import (
    Project,
    SavedProject,
    ProjectType,
    does_project_exist_at_path
)

from cuhkit.exceptions import (
    ProjectAlreadyExistsException
)

# // Main
__all__ = [
    "SavedAddonProject",
    "AddonProject",
    "create_addon_project"
]

class SavedAddonProject(SavedProject):
    """
    A saved cuhkit addon project.
    """

    project_type: ProjectType = ProjectType.ADDON

class AddonProject(Project):
    """
    A cuhkit addon project.
    """
    
    def __init__(self, name: str, path: str):
        """
        Initialises cuhkit addon projects.

        Args:
            name (str): The name of the addon project.
            path (str): The path to the addon project.
        """

        super().__init__(
            name = name,
            project_type = ProjectType.ADDON,
            path = path
        )
        
    def get_saved_project(self) -> SavedAddonProject:
        """
        Returns a saved cuhkit addon project for this addon project.

        Returns:
            SavedAddonProject: The saved cuhkit addon project.
        """

        return SavedAddonProject(
            name = self.name,
            path = self.path
        )
        
    @staticmethod
    def get_saved_project_from_content(content: str) -> SavedAddonProject:
        """
        Returns a saved cuhkit addon project from the content of a cuhkit project file.

        Args:
            content (str): The content of the cuhkit project file.
            
        Returns:
            SavedAddonProject: The saved cuhkit addon project.
        """

        return SavedAddonProject.model_validate_strings(content)
    
    @classmethod
    def from_saved_project(cls, saved_project: SavedAddonProject) -> AddonProject:
        """
        Creates a cuhkit addon project from a saved cuhkit addon project.

        Args:
            saved_project (SavedAddonProject): The saved cuhkit addon project to create the cuhkit addon project from.
            
        Returns:
            AddonProject: The created cuhkit addon project.
        """
        
        return cls(
            name = saved_project.name,
            path = saved_project.path
        )

def create_addon_project(name: str, path: str) -> Project:
    """
    Creates a cuhkit addon project.

    Args:
        name (str): The name of the addon project.
        path (str): The path to the directory to create the addon project in.
    
    Raises:
        ValueError: If the path is not a directory.
        ProjectAlreadyExistsException: If a cuhkit project already exists at the path.

    Returns:
        Project: The created cuhkit addon project.
    """

    if not os.path.isdir(path):
        raise ValueError(f"Path must be a directory: {path}")
    
    if does_project_exist_at_path(path):
        raise ProjectAlreadyExistsException(f"A cuhkit project already exists at path: {path}")
    
    return AddonProject(
        name = name,
        path = path
    )