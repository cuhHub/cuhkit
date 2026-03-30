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
from enum import Enum

from pydantic import (
    BaseModel,
    ValidationError
)

from cuhkit.exceptions import (
    ProjectNotFoundException,
    ProjectLoadFailureException,
    ProjectAlreadyExistsException
)

# // Main
__all__ = [
    "ProjectType",
    "SavedProject",
    "Project",
    "does_project_exist_at_path"
]

class ProjectType(Enum):
    """
    Enum representing the type of a cuhkit project.
    """

    ADDON = "addon"
    MOD = "mod"

class SavedProject(BaseModel):
    """
    A saved cuhkit project.
    """

    name: str
    project_type: ProjectType
    path: str

class Project():
    """
    A cuhkit project.
    """
    
    CUHKIT_PROJECT_FILE_NAME = ".cuhkitproj.json"
    
    def __init__(self, name: str, project_type: ProjectType, path: str):
        """
        Initialises cuhkit projects.

        Args:
            name (str): The name of the project.
            project_type (ProjectType): The type of the project.
            path (str): The path to the project.
            
        Raises:
            ProjectAlreadyExistsException: If a cuhkit project already exists at the
        """
        
        if does_project_exist_at_path(path):
            raise ProjectAlreadyExistsException(f"A cuhkit project already exists at path: {path}")
        
        self.name = name
        self.project_type = project_type
        self.path = os.path.abspath(path)
        self.saved_project = self.get_saved_project()
        
        self.save()
        
    def _get_path_to_project_file(self) -> str:
        """
        Gets the path to the cuhkit project file for this project.

        Returns:
            str: The path to the cuhkit project file for this project.
        """

        return os.path.join(self.path, self.CUHKIT_PROJECT_FILE_NAME)
        
    def get_saved_project(self) -> SavedProject:
        """
        Returns a saved cuhkit project for this project.

        Returns:
            SavedProject: The saved cuhkit project.
        """

        raise NotImplementedError("Project.get_saved_project is not implemented.")
    
    def save(self):
        """
        Saves this cuhkit project.
        """
        
        with open(self._get_path_to_project_file(), "w") as file:
            file.write(self.saved_project.model_dump_json(indent = 7))
            
    @staticmethod
    def get_saved_project_from_content(content: str) -> SavedProject:
        """
        Returns a saved cuhkit project from the content of a cuhkit project file.

        Args:
            content (str): The content of the cuhkit project file.
            
        Returns:
            SavedProject: The saved cuhkit project.
        """
        
        raise NotImplementedError("Project.get_saved_project_from_content is not implemented.")
            
    @classmethod
    def from_saved_project(cls, saved_project: SavedProject) -> Project:
        """
        Creates a cuhkit project from a saved cuhkit project.

        Args:
            saved_project (SavedProject): The saved cuhkit project to create the cuhkit project from.
            
        Returns:
            Project: The created cuhkit project.
        """

        raise NotImplementedError("Project.from_saved_project is not implemented.")
    
    @classmethod
    def from_path(cls, path: str):
        """
        Creates a cuhkit project from a path to the directory of a cuhkit project.
        
        Args:
            path (str): The path to the directory of the cuhkit project.
            
        Raises:
            ProjectNotFoundException: If no cuhkit project file is found at the path.
            ProjectLoadFailureException: If the cuhkit project file could not be loaded.
            
        Returns:
            Project: The created cuhkit project.
        """
        
        project_file_path = os.path.join(path, cls.CUHKIT_PROJECT_FILE_NAME) if os.path.isdir(path) else path
        
        if not does_project_exist_at_path(project_file_path):
            raise ProjectNotFoundException(f"No cuhkit project file found at path: {project_file_path}")
        
        with open(project_file_path, "r") as file:
            content = file.read()
            
        try:
            saved_project = cls.get_saved_project_from_content(content)
        except ValidationError as exception:
            raise ProjectLoadFailureException(f"Failed to load cuhkit project from file at path: {project_file_path}") from exception

        return cls.from_saved_project(saved_project)

def does_project_exist_at_path(path: str) -> bool:
    """
    Checks if a cuhkit project exists at a path.

    Args:
        path (str): The path to check for a cuhkit project.

    Returns:
        bool: True if a cuhkit project exists at the path, False otherwise.
    """
    
    if os.path.isfile(path):
        return os.path.basename(path) == Project.CUHKIT_PROJECT_FILE_NAME
    elif os.path.isdir(path):
        return os.path.isfile(os.path.join(path, Project.CUHKIT_PROJECT_FILE_NAME))

    return False