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
import shutil
from pathlib import Path

from pydantic import (
    BaseModel,
    Field
)

from cuhkit.log import logger

from cuhkit.libs.requests import (
    request,
    requests,
    is_plain_text_response
)

# // Main
METADATA_FILE_NAME = ".build.json"

class WebImport(BaseModel):
    """
    A model for a web import.
    """
    
    url: str
    name: str

class BuilderMetadata(BaseModel):
    """
    A model for builder metadata in a directory.
    """
    
    build_order: list[Path] | None = None
    ignore: list[Path] = Field(default_factory = list)
    import_web: list[WebImport] = Field(default_factory = list)
    import_local: list[Path] = Field(default_factory = list)
    
    def resolve_build_order(self, root: Path) -> list[Path]:
        """
        Resolves the build order paths relative to the root directory.

        Args:
            root (Path): The root directory of the project.

        Returns:
            list[Path]: The resolved build order paths.
        """
        
        return [root / path for path in self.build_order]
    
    def resolve_ignores(self, root: Path) -> list[Path]:
        """
        Resolves the ignore paths relative to the root directory.

        Args:
            root (Path): The root directory of the project.

        Returns:
            list[Path]: The resolved ignore paths.
        """
        
        return [root / path for path in self.ignore]
    
    def handle_paths(self, root: Path, paths: list[Path]) -> list[Path]:
        """
        Handles a list of paths according to the metadata (reordering, ignoring, etc.).

        Args:
            root (Path): The root directory of the paths.
            paths (list[Path]): The list of paths to handle.

        Returns:
            list[Path]: The handled list of paths.
        """
        
        handled_paths: list[Path] = []
        ignore = self.resolve_ignores(root)

        if self.build_order:
            for path in self.resolve_build_order(root):
                if not path.exists():
                    logger.error(f"BuilderMetadata: Path in `build_order` does not exist. Ignoring. Path: {path}")
                    continue
                
                if is_path_in_list(path, ignore):
                    continue
                
                if is_path_in_list(path, handled_paths):
                    continue
                
                handled_paths.append(path)
        else:
            for path in paths:
                if is_path_in_list(path, ignore):
                    continue
                
                handled_paths.append(path)
                    
        return handled_paths
    
    def handle_local_imports(self, destination_directory: Path):
        """
        Handles importing local files/directories specified in the metadata to a destination directory.

        Args:
            destination_directory (Path): The directory to import the local files/directories to.
        """
        
        for path in self.import_local:
            if not path.exists():
                logger.error(f"Failed to import local file/directory at path: {path} (path does not exist)")
                continue

            if path.is_dir():
                destination = destination_directory / path.name

                if destination.exists():
                    shutil.rmtree(destination)
                
                shutil.copytree(path, destination, dirs_exist_ok = True)
            else:
                shutil.copy2(path, destination_directory)
                
    def _handle_web_import(self, web_import: WebImport, destination_directory: Path):
        """
        Handles a web import.

        Args:
            web_import (WebImport): The web import to handle.
            destination_directory (Path): The directory to import the web file to.
        """
        
        logger.debug(f"addon_builder: Importing web file at URL: {web_import.url} (name: {web_import.name})")
        
        try:
            response = request("GET", web_import.url)
            response.raise_for_status()
        except requests.exceptions.RequestException as exception:
            logger.error(f"Failed to import web file/directory at URL: {web_import.url} (request error, exception: {exception})")
            return
        except requests.exceptions.HTTPError as exception:
            logger.error(f"Failed to import web file/directory at URL: {web_import.url} (HTTP error (bad status code), exception: {exception})")
            return
        
        if not is_plain_text_response(response):
            logger.error(f"Failed to import web file/directory at URL: {web_import.url} (content type is not text/plain, got: {response.headers.get("content-type")})")
            return
        
        destination = destination_directory / (web_import.name + ".lua")
        destination.write_text(response.text)
                
    def handle_web_imports(self, destination_directory: Path):
        """
        Handles all web imports.
        
        Args:
            destination_directory (Path): The directory to import the web files to.
        """

        for web_import in self.import_web:
            self._handle_web_import(web_import, destination_directory)
    
def is_path_in_list(path: Path, paths: list[Path]) -> bool:
    """
    Checks if a path is in a list of paths.

    Args:
        path (Path): The path to check.
        paths (list[Path]): The list of paths to check against.

    Returns:
        bool: True if the path is in the list of paths, False otherwise.
    """
    
    resolved_paths = [p.resolve() for p in paths]
    resolved_path = path.resolve()
    
    return resolved_path in resolved_paths

def get_expected_metadata_path(path: Path) -> Path:
    """
    Gets the expected path to builder metadata in a directory.

    Args:
        path (Path): The directory to get the expected metadata path for.

    Returns:
        Path: The expected path to builder metadata in the directory.
    """
    
    return path / METADATA_FILE_NAME
    
def does_metadata_exist(path: Path) -> bool:
    """
    Checks if builder metadata exists at a path.

    Args:
        path (Path): The path to check for builder metadata.

    Returns:
        bool: True if builder metadata exists at the path, False otherwise.
    """
    
    return get_expected_metadata_path(path).exists()
    
def load_metadata(path: Path) -> BuilderMetadata:
    """
    Loads builder metadata from a directory.

    Args:
        path (Path): The directory to load metadata from.

    Returns:
        BuilderMetadata: The loaded builder metadata.
    """

    if not does_metadata_exist(path):
        logger.debug(f"addon_builder: Using default metadata as no metadata at: {path}")
        return BuilderMetadata()

    logger.debug(f"addon_builder: Using metadata at: {path}")

    metadata_file = get_expected_metadata_path(path)
    return BuilderMetadata.model_validate_json(metadata_file.read_text())
    
def handle_content(root_directory: Path, file_path: Path, file_content: str) -> str:
    """
    Handles the content of a file for building.

    Args:
        root_directory (Path): The root directory of the project.
        file_path (Path): The path to the file.
        file_content (str): The content of the file to handle.

    Returns:
        str: The handled content of the file.
    """
    
    relative_path = file_path.relative_to(root_directory)
    return f"-- cuhkit: {relative_path}\n{file_content}"
    
def build_directory(directory: Path, ignore: list[Path]) -> list[str]:
    """
    Recursively builds all .lua files inside the provided directory.

    Args:
        directory (Path): The directory to build.
        ignore (list[Path]): A list of paths to ignore while building.

    Returns:
        list[str]: The combined content of the directory.
    """

    content: list[str] = []

    metadata = load_metadata(directory)
    metadata.handle_local_imports(directory)
    metadata.handle_web_imports(directory)
    
    paths = metadata.handle_paths(directory, list(directory.iterdir()))
    
    for path in paths:
        if is_path_in_list(path, ignore):
            logger.debug(f"addon_builder: Ignoring path: {path}")
            continue
        
        logger.debug(f"addon_builder: Handling path: {path}")

        if path.is_dir():
            logger.debug(f"addon_builder: Path is directory, entering")
            content.extend(build_directory(path, ignore))
            continue
        
        if path.suffix != ".lua":
            logger.debug(f"addon_builder: Ignoring, not a .lua file")
            continue
        
        logger.debug(f"addon_builder: Building file")
        content.append(handle_content(directory, path, path.read_text()))

    return content
    
def build_addon(directory: Path, output_file: Path):
    """
    Builds all addon .lua files into a single .lua file at the specified output path.

    Args:
        directory (Path): The directory to build the addon from.
        output_path (Path): The file to output the built addon to.
    """
    
    content: str = "\n\n\n".join(build_directory(directory, ignore = [output_file]))
    output_file.parent.mkdir(parents = True, exist_ok = True)

    logger.debug(f"addon_builder: Writing build to output path: {output_file}")
    output_file.write_text(content)
    
def get_vehicle_files(directory: Path) -> list[Path]:
    """
    Returns all vehicle files in the given directory.

    Args:
        directory (Path): The directory to get the vehicle files from.

    Returns:
        list[Path]: The list of vehicle files in the directory.
    """
    
    return list(directory.glob("vehicle_*.xml"))

def _copy_stormworks_to_addon(addon_project_directory: Path, stormworks_addon_directory: Path):
    """
    Copies down necessary files from Stormworks addon directory to addon project directory (playlist, vehicles, etc.).

    Args:
        addon_project_directory (Path): The addon project directory.
        stormworks_addon_directory (Path): The path of the Stormworks addon.
        
    Raises:
        ValueError: If the provided Stormworks addon directory does not exist.
        FileNotFoundError: If the addon playlist file does not exist in the Stormworks addon directory.
    """
    
    if not stormworks_addon_directory.exists():
        raise ValueError("Bad `stormworks_addon_directory`. Directory does not exist.")
    
    playlist_file = stormworks_addon_directory / "playlist.xml"

    if not playlist_file.exists():
        raise FileNotFoundError("Missing `playlist.xml` file in Stormworks addon directory.")
    
    shutil.copy2(playlist_file, addon_project_directory)
    
    logger.debug(f"addon_builder: Removing vehicles from addon project (will be re-added)")

    for vehicle_file in get_vehicle_files(addon_project_directory):
        vehicle_file.unlink()
    
    logger.debug(f"addon_builder: Copying vehicles from Stormworks addon to addon project")

    for vehicle_file in get_vehicle_files(stormworks_addon_directory):
        shutil.copy2(vehicle_file, addon_project_directory)
        
    logger.debug(f"addon_builder: Copying playlist from Stormworks addon to addon project")
    
def setup_addon(addon_project_directory: Path, addon_code_file: Path, stormworks_addon_directory: Path):
    """
    Sets up an addon project by copying files that should be in Stormworks addon directory from the addon project directory.
    This should be used to set up an addon project for the first time after cloning it, otherwise just create an addon in-game
    with the same name as the addon project.

    Args:
        addon_project_directory (Path): The addon project directory.
        addon_code_file (Path): The path to the full addon code for the Stormworks addon.
        stormworks_addon_directory (Path): The path of the Stormworks addon.
        
    Raises:
        FileNotFoundError: If the addon playlist file does not exist in the addon directory.
    """
    
    logger.debug(f"addon_builder: Copying vehicles to Stormworks addon")
    stormworks_addon_directory.mkdir(parents = True, exist_ok = True)
    
    for vehicle_file in get_vehicle_files(addon_project_directory):
        shutil.copy2(vehicle_file, stormworks_addon_directory)
        
    logger.debug(f"addon_builder: Copying playlist to Stormworks addon")
    playlist_file = addon_project_directory / "playlist.xml"

    if not playlist_file.exists():
        raise FileNotFoundError("Missing `playlist.xml` file in addon project directory.")
    
    shutil.copy2(playlist_file, stormworks_addon_directory)
    
    logger.debug(f"addon_builder: Copying addon code to Stormworks addon")
    shutil.copy2(addon_code_file, stormworks_addon_directory / "script.lua")
    
def sync_addon(addon_project_directory: Path, addon_code_file: Path, stormworks_addon_directory: Path):
    """
    Syncs an addon with Stormworks so it can be used in-game.

    Args:
        addon_project_directory (Path): The addon project directory.
        addon_code_file (Path): The path to the full addon code for the Stormworks addon.
        stormworks_addon_directory (Path): The path of the Stormworks addon.
        
    Raises:
        FileNotFoundError: If an addon playlist file does not exist in the addon directory.
        ValueError: If the provided Stormworks addon directory does not exist.
    """
    
    if not stormworks_addon_directory.exists():
        raise ValueError("Bad `stormworks_addon_directory`. Directory does not exist.")
    
    logger.debug(f"addon_builder: Copying addon code to Stormworks addon")
    shutil.copy2(addon_code_file, stormworks_addon_directory / "script.lua")
    
    _copy_stormworks_to_addon(addon_project_directory, stormworks_addon_directory)