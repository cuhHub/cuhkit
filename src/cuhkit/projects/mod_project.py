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
    "SavedModProject",
    "ModProject",
    "create_mod_project"
]

class SavedModProject(SavedProject):
    """
    A saved cuhkit mod project.
    """

    project_type: ProjectType = ProjectType.MOD

class ModProject(Project):
    """
    A cuhkit mod project.
    """
    
    def __init__(self, name: str, path: str):
        """
        Initialises cuhkit mod projects.

        Args:
            name (str): The name of the mod project.
            path (str): The path to the mod project.
        """

        super().__init__(
            name = name,
            project_type = ProjectType.MOD,
            path = path
        )
        
    def get_saved_project(self) -> SavedModProject:
        """
        Returns a saved cuhkit mod project for this mod project.

        Returns:
            SavedModProject: The saved cuhkit mod project.
        """

        return SavedModProject(
            name = self.name,
            path = self.path
        )
        
    @staticmethod
    def get_saved_project_from_content(content: str) -> SavedModProject:
        """
        Returns a saved cuhkit mod project from the content of a cuhkit project file.

        Args:
            content (str): The content of the cuhkit project file.
            
        Returns:
            SavedModProject: The saved cuhkit mod project.
        """

        return SavedModProject.model_validate_strings(content)
    
    @classmethod
    def from_saved_project(cls, saved_project: SavedModProject) -> ModProject:
        """
        Creates a cuhkit mod project from a saved cuhkit mod project.

        Args:
            saved_project (SavedModProject): The saved cuhkit mod project to create the cuhkit mod project from.
            
        Returns:
            ModProject: The created cuhkit mod project.
        """
        
        return cls(
            name = saved_project.name,
            path = saved_project.path
        )

def create_mod_project(name: str, path: str) -> Project:
    """
    Creates a cuhkit mod project.

    Args:
        name (str): The name of the mod project.
        path (str): The path to the directory to create the mod project in.
        
    Raises:
        ValueError: If the path is not a directory.
        ProjectAlreadyExistsException: If a cuhkit project already exists at the path.

    Returns:
        Project: The created cuhkit mod project.
    """

    if not os.path.isdir(path):
        raise ValueError(f"Path must be a directory: {path}")
    
    if does_project_exist_at_path(path):
        raise ProjectAlreadyExistsException(f"A cuhkit project already exists at path: {path}")
    
    return ModProject(
        name = name,
        path = path
    )