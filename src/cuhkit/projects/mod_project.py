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
    does_project_exist_at_path,
    TEMPLATES_PATH
)

from cuhkit.exceptions import (
    ProjectAlreadyExistsException,
    CredentialsException
)

from cuhkit.libs import mod_builder
from cuhkit.libs import templates
from cuhkit.libs.timeit import TimeIt
from cuhkit.log import logger

# // Main
__all__ = [
    "ModProjectConfiguration",
    "ModProject",
    "create_mod_project"
]

MOD_TEMPLATE_PATH = TEMPLATES_PATH / "mod_template"
INTELLISENSE_GITHUB_URL = "https://raw.githubusercontent.com/Cuh4/StormworksModLuaDocumentation/main/docs/intellisense.lua"

class ModProjectConfiguration(ProjectConfiguration):
    """
    A mod project configuration.
    """

    project_type: ProjectType = ProjectType.MOD
    mod_build_destination: Path = Path(".build/mod.zip")
    stormworks_mods_path: Path | None = None

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
        
    def first_time_setup(self):
        """
        Setups the mod project (first-time setup).
        This should only need to be used after creating a mod project.
        """
        
        templates.copy_template(
            template_path = MOD_TEMPLATE_PATH,
            downloads = [
                templates.TemplateDownload(
                    url = INTELLISENSE_GITHUB_URL,
                    destination = self.project_configuration.path / "intellisense.lua"
                )
            ],
            destination = self.project_configuration.path
        )
        
    def get_stormworks_mod_directory(self) -> Path:
        """
        Returns the Stormworks mod path for this project.
        
        Raises:
            FileNotFoundError: If the default Stormworks mod directory could not be found.

        Returns:
            Path: The path to the Stormworks mod.
        """
        
        if self.project_configuration.stormworks_mods_path is None:
            path = Path(os.environ["APPDATA"]) / "Stormworks" / "data" / "mods"
            
            if not path.exists():
                raise FileNotFoundError(f"Default Stormworks mod directory not found. Consider setting `stormworks_mods_path` in the project configuration.")
            
            return path / self.name

        return self.project_configuration.stormworks_mods_path / self.name
     
    def build(self):
        """
        Builds the mod project for publishing.
        """
        
        logger.info(f"Building mod in {self.project_configuration.src} to {self.project_configuration.mod_build_destination}...")
        
        with TimeIt():
            mod_builder.build_mod(self.project_configuration.src, self.project_configuration.mod_build_destination)

    def sync(self):
        """
        Syncs the mod to the game.
        """
        
        logger.info(f"Syncing to game ({self.get_stormworks_mod_directory()})...")

        with TimeIt():
            mod_builder.sync_mod(self.project_configuration.src, self.get_stormworks_mod_directory())
            
    def publish(self, server_id: int, is_dev: bool = False):
        """
        Publishes the mod to cuhHub.
        
        Args:
            server_id (int): The server ID to publish to, or -1 for all.
            is_dev (bool): Whether or not to publish as a development build.
        
        Raises:
            CredentialsException: If no API token is found in credentials
        """

        if self.api_client is None:
            raise CredentialsException("No API token found in credentials, can't publish.")
        
        mod_name = self.get_publish_name(is_dev)
        logger.info(f"Uploading mod to cuhHub as '{mod_name}'...")
        
        if not self.project_configuration.mod_build_destination.exists():
            logger.info("Mod build not found, building...")
            self.build()
            
        with TimeIt():
            self.api_client.upload_mod(mod_name, self.project_configuration.mod_build_destination)
            
        server_ids = self.get_publish_server_ids(server_id)
        logger.info(f"Adding mod to server: {server_ids}")
        
        with TimeIt():
            for server_id in server_ids:
                if not self.api_client.is_mod_in_server(mod_name, server_id):
                    logger.info(f"Adding mod to server {server_id}...")
                    self.api_client.add_mod(mod_name, server_id)
                else:
                    logger.info(f"Mod already in server {server_id}, skipping...")
                    
            logger.info(f"Refreshing server {server_id}...")
            self.api_client.refresh_server(server_id)

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