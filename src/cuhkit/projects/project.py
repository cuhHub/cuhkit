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

from pathlib import Path
from enum import Enum

from pydantic import (
    BaseModel,
    ValidationError
)

from cuhkit.exceptions import (
    ProjectNotFoundException,
    ProjectLoadFailureException
)

from cuhkit.libs.api import Client
from cuhkit.credentials import credentials

# // Main
__all__ = [
    "ProjectType",
    "ProjectConfiguration",
    "Project",
    "get_project_file_path",
    "does_project_exist_at_path"
]

class ProjectType(Enum):
    """
    Enum representing the type of a cuhkit project.
    """

    ADDON = "addon"
    MOD = "mod"

class ProjectConfiguration(BaseModel):
    """
    A base cuhkit project configuration.
    """

    name: str
    project_type: ProjectType
    path: Path
    src: Path = None
    
    def model_post_init(self, context = None):
        """
        Callback for model post initialisation.
        """
        
        if self.src is not None:
            return
        
        self.src = self.path / "src"

class Project():
    """
    A base cuhkit project.
    """
    
    CUHKIT_PROJECT_FILE_NAME = ".cuhkitproj.json"
    
    def __init__(self, name: str, project_type: ProjectType, path: Path):
        """
        Initialises cuhkit projects.

        Args:
            name (str): The name of the project.
            project_type (ProjectType): The type of the project.
            path (Path): The path to the project.
        """

        self.name = name
        self.project_type = project_type
        self.path = path.resolve()
        self.project_configuration = None
        
        self.api_client = Client(token = credentials.api_token) if credentials.api_token is not None else None

    def get_path_to_project_file(self) -> Path:
        """
        Gets the path to the cuhkit project file for this project.

        Returns:
            Path: The path to the cuhkit project file for this project.
        """

        return get_project_file_path(self.path)
        
    def get_project_configuration(self) -> ProjectConfiguration:
        """
        Returns the project configuration for this project.

        Returns:
            ProjectConfiguration: The project configuration.
        """

        raise NotImplementedError("Project.get_project_configuration is not implemented.")
    
    def save(self):
        """
        Saves this cuhkit project to a project configuration file.
        """
        
        self.get_path_to_project_file().write_text(self.project_configuration.model_dump_json(indent = 3))
            
    def delete(self):
        """
        Deletes the cuhkit project configuration file.
        """

        self.get_path_to_project_file().unlink(missing_ok = True)
            
    @staticmethod
    def get_project_configuration_from_content(content: str) -> ProjectConfiguration:
        """
        Returns a project configuration from the content of a cuhkit project file.

        Args:
            content (str): The content of the cuhkit project file.
            
        Returns:
            ProjectConfiguration: The project configuration.
        """
        
        raise NotImplementedError("Project.get_project_configuration_from_content is not implemented.")
            
    @classmethod
    def from_project_configuration(cls, project_configuration: ProjectConfiguration) -> Project:
        """
        Creates a cuhkit project from a project configuration.

        Args:
            project_configuration (ProjectConfiguration): The project configuration to create the cuhkit project from.
            
        Returns:
            Project: The created cuhkit project.
        """

        raise NotImplementedError("Project.from_project_configuration is not implemented.")
    
    @classmethod
    def from_path(cls, path: Path) -> Project:
        """
        Creates a cuhkit project from a path to the directory of a cuhkit project.
        
        Args:
            path (Path): The path to the directory of the cuhkit project.
            
        Raises:
            ProjectNotFoundException: If no cuhkit project file is found at the path.
            ProjectLoadFailureException: If the cuhkit project file could not be loaded.
            
        Returns:
            Project: The created cuhkit project.
        """
        
        project_file_path = get_project_file_path(path) if path.is_dir() else path
        
        if not does_project_exist_at_path(project_file_path):
            raise ProjectNotFoundException(f"No cuhkit project file found at path: {project_file_path}")
        
        content = project_file_path.read_text()
            
        try:
            project_configuration = cls.get_project_configuration_from_content(content)
        except ValidationError as exception:
            raise ProjectLoadFailureException(f"Failed to load cuhkit project from file at path: {project_file_path}") from exception

        return cls.from_project_configuration(project_configuration)

def get_project_file_path(path: Path) -> Path:
    """
    Gets the path to the cuhkit project file in a directory.

    Args:
        path (Path): The directory to get the cuhkit project file path in.

    Returns:
        Path: The path to the cuhkit project file in the directory.
    """

    return path / Project.CUHKIT_PROJECT_FILE_NAME

def does_project_exist_at_path(path: Path) -> bool:
    """
    Checks if a cuhkit project exists at a path.

    Args:
        path (Path): The path to check for a cuhkit project.

    Returns:
        bool: True if a cuhkit project exists at the path, False otherwise.
    """
    
    if path.is_file():
        return path.name == Project.CUHKIT_PROJECT_FILE_NAME
    elif path.is_dir():
        return get_project_file_path(path).is_file()

    return False