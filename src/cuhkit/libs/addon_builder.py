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

# // Main
METADATA_FILE_NAME = ".build.json"

class BuilderMetadata(BaseModel):
    """
    A model for builder metadata in a directory.
    """
    
    build_order: list[Path] | None = None
    ignore: list[Path] = Field(default_factory = list)
    import_web: list[str] = Field(default_factory = list)
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
                
    def handle_web_imports(self, destination_directory: Path):
        """
        Handles importing web files/directories specified in the metadata to a destination directory.
        
        Args:
            destination_directory (Path): The directory to import the web files to.
        """

        pass # todo
    
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