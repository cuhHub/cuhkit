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

from abc import ABC, abstractmethod
from pathlib import Path
from enum import Enum

from pydantic import (
    BaseModel,
    ValidationError
)

from typing import Generic, TypeVar

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
        
TProjectConfiguration = TypeVar("TProjectConfiguration", bound = ProjectConfiguration) # shoot me dude

class Project(Generic[TProjectConfiguration], ABC):
    """
    A base cuhkit project.
    """
    
    CUHKIT_PROJECT_FILE_NAME = ".cuhkitproj.json"
    
    def __init__(self, project_configuration: TProjectConfiguration = None):
        """
        Initialises cuhkit projects.

        Args:
            project_configuration (TProjectConfiguration): The cuhkit project configuration
        """

        self.project_configuration = project_configuration
        self.api_client = Client(token = credentials.api_token) if credentials.api_token is not None else None

    @property
    def name(self) -> str:
        """
        Gets the name of this project.

        Returns:
            str: The name of this project.
        """

        return self.project_configuration.name
    
    @property
    def project_type(self) -> ProjectType:
        """
        Gets the type of this project.

        Returns:
            ProjectType: The type of this project.
        """
        
        return self.project_configuration.project_type
    
    @property
    def path(self) -> Path:
        """
        Gets the path to the project's directory.

        Returns:
            Path: The path to the project's directory.
        """

        return self.project_configuration.path
    
    @property
    def src(self) -> Path:
        """
        Gets the path to the source directory for this project.

        Returns:
            Path: The path to the source directory for this project.
        """
        
        return self.project_configuration.src
    
    @abstractmethod
    def first_time_setup(self):
        """
        Setups the project (first-time setup).
        This should only need to be used after creating the project.
        """

        pass
        
    def get_publish_name(self, is_dev: bool) -> str:
        """
        Returns the project name for publishing.
        
        Args:
            is_dev (bool): Whether or not to return the development build name.
            
        Returns:
            str: The name of the published project.
        """

        if is_dev:
            return f"{self.name}_dev"

        return self.name
    
    def get_publish_server_ids(self, server_id: int) -> list[int]:
        """
        Returns the server IDs to publish to.
        
        Args:
            server_id (int): The server ID to publish to, or -1 for all.
            
        Returns:
            list[int]: The server IDs to publish to.
        """

        if server_id == -1:
            return [server["id"] for server in self.api_client.get_servers()]
        
        return [server_id]

    def get_path_to_project_file(self) -> Path:
        """
        Gets the path to the cuhkit project file for this project.

        Returns:
            Path: The path to the cuhkit project file for this project.
        """

        return get_project_file_path(self.path)

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
    @abstractmethod
    def get_project_configuration_from_content(content: str) -> ProjectConfiguration:
        """
        Returns a project configuration from the content of a cuhkit project file.

        Args:
            content (str): The content of the cuhkit project file.
            
        Returns:
            ProjectConfiguration: The project configuration.
        """
        
        pass
    
    @classmethod
    def from_path(cls, path: Path) -> Project:
        """
        Creates a cuhkit project from a path to a cuhkit project.
        
        Args:
            path (Path): The path to the cuhkit project.
            
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

        return cls(project_configuration)

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