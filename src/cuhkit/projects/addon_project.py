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
import requests
import shutil

from . import (
    Project,
    ProjectConfiguration,
    ProjectType,
    does_project_exist_at_path
)

from cuhkit.exceptions import (
    ProjectAlreadyExistsException
)

from cuhkit import CUHKIT_PACKAGE_PATH
from cuhkit.libs import addon_builder
from cuhkit.libs.timeit import TimeIt
from cuhkit.log import logger

# // Main
__all__ = [
    "AddonProjectConfiguration",
    "AddonProject",
    "create_addon_project"
]

ADDON_TEMPLATE_PATH = CUHKIT_PACKAGE_PATH / "projects" / "addon_template"
INTELLISENSE_GITHUB_URL = "https://raw.githubusercontent.com/Cuh4/StormworksAddonLuaDocumentation/main/docs/intellisense.lua"

class AddonProjectConfiguration(ProjectConfiguration):
    """
    An addon project configuration.
    """

    project_type: ProjectType = ProjectType.ADDON
    build_destination: Path = Path(".build/addon.lua")
    stormworks_addons_path: Path = Path(os.environ["APPDATA"]) / "Stormworks" / "data" / "missions"

class AddonProject(Project[AddonProjectConfiguration]):
    """
    A cuhkit addon project.
    """
    
    def __init__(self, project_configuration: AddonProjectConfiguration):
        """
        Initialises cuhkit addon projects.

        Args:
            project_configuration (AddonProjectConfiguration): The cuhkit addon project configuration
        """

        super().__init__(
            project_configuration = project_configuration
        )
 
    def get_stormworks_addon_directory(self) -> Path:
        """
        Returns the Stormworks addon path for this project.

        Returns:
            Path: The path to the Stormworks addon.
        """

        return self.project_configuration.stormworks_addons_path / self.name
    
    def copy_over_template(self):
        """
        Copies over the addon template to the project.
        """
        
        logger.info(f"Copying over addon template ({ADDON_TEMPLATE_PATH}) to {self.project_configuration.path}...")
        shutil.copytree(ADDON_TEMPLATE_PATH, self.project_configuration.path, dirs_exist_ok = True)
        
        intellisense_file = self.project_configuration.path / "intellisense.lua"
        intellisense_file.write_text(requests.get(INTELLISENSE_GITHUB_URL).text)
        
    def first_time_setup(self):
        """
        Setups the addon project (first-time setup).
        This should only need to be used after creating an addon project.
        """
        
        self.copy_over_template()
    
    def setup(self):
        """
        Setups the addon project (first-time setup).
        This should only need to be used after cloning an addon project.
        """
        
        self.build()
        
        logger.info("Setting up addon project...")
        
        try:
            addon_builder.setup_addon(self.project_configuration.src, self.project_configuration.build_destination, self.get_stormworks_addon_directory())
        except FileNotFoundError:
            logger.error("Failed to setup addon project, missing `playlist.xml` file in addon src directory.")
         
    def build(self):
        """
        Builds the addon project.
        """

        logger.info(f"Building .lua files in {self.project_configuration.src} to {self.project_configuration.build_destination}...")       

        with TimeIt(): 
            addon_builder.build_addon(self.project_configuration.src, self.project_configuration.build_destination)
            
    def _get_published_addon_name(self, is_dev: bool) -> str:
        """
        Returns the name of the published addon.
        
        Args:
            is_dev (bool): Whether or not to return the development build name.
            
        Returns:
            str: The name of the published addon.
        """

        if is_dev:
            return f"{self.name}_dev"

        return self.name
    
    def _get_publish_server_ids(self, server_id: int) -> list[int]:
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
            
    def publish(self, server_id: int = -1, is_dev: bool = False):
        """
        Publishes the addon project to cuhHub.
        
        Args:
            server_id (int): The server ID to publish to, or -1 for all.
            is_dev (bool): Whether or not to publish as a development build.
            
        Raises:
            ValueError: If no API token is found in credentials
            FileNotFoundError: If the addon playlist file could not be found
        """
        
        if self.api_client is None:
            raise ValueError("No API token found in credentials, can't publish.")
        
        addon_name = self._get_published_addon_name(is_dev)
        logger.info(f"Uploading addon to cuhHub as '{addon_name}'...")
        
        if not self.project_configuration.build_destination.exists():
            logger.info("Addon build not found, building...")
            self.build()
            
        playlist_file = self.project_configuration.src / "playlist.xml"
        
        if not playlist_file.exists():
            raise FileNotFoundError("Missing `playlist.xml` file in addon project src directory.")
        
        with TimeIt():
            self.api_client.upload_addon(
                addon_name = addon_name,
                script_file = self.project_configuration.build_destination,
                playlist_file = playlist_file,
                vehicle_files = addon_builder.get_vehicle_files(self.project_configuration.src),
                allow_update = True
            )
        
        server_ids = self._get_publish_server_ids(server_id)
        logger.info(f"Adding addon to servers: {server_ids}...")
        
        with TimeIt():
            for server_id in server_ids:
                if not self.api_client.is_addon_in_server(addon_name, server_id):
                    logger.info(f"Adding addon to server {server_id}...")
                    self.api_client.add_addon(addon_name, server_id)
                else:
                    logger.info("Addon already in server, no need to add.")
                    
                logger.info(f"Refreshing server {server_id}...")
                self.api_client.refresh_server(server_id)
        
    def sync(self):
        """
        Syncs the addon to the game.
        """
        
        logger.info(f"Syncing to game ({self.get_stormworks_addon_directory()})...")
        
        try:
            with TimeIt():
                addon_builder.sync_addon(
                    addon_project_directory = self.project_configuration.src,
                    addon_code_file = self.project_configuration.build_destination,
                    stormworks_addon_directory = self.get_stormworks_addon_directory()
                )
        except FileNotFoundError as exception:
            logger.error(f"Failed to sync addon, got exception: {exception}")
            logger.info("This may be due to a missing `playlist.xml` file in the Stormworks addon directory. Please set up this addon project first to try and automatically create the `playlist.xml` file, or manually create one if not doable.")
        
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
        project_configuration = AddonProjectConfiguration(
            name = name,
            path = path
        )
    )