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

# // Main
import json
from pathlib import Path

from cuhkit import CUHKIT_PACKAGE_PATH
TEMPLATES_PATH = CUHKIT_PACKAGE_PATH / "projects" / "templates"

if not TEMPLATES_PATH.exists():
    raise RuntimeError(f"Could not find templates directory: {TEMPLATES_PATH}")

from .project import *
from .mod_project import *
from .addon_project import *

from cuhkit.exceptions import (
    ProjectNotFoundException,
    ProjectLoadFailureException
)

def load_project_at_path(path: Path) -> AddonProject | ModProject:
    """
    Loads a cuhkit project at the specified path.
    
    Args:
        path (Path): The directory the project is in, or path to the project file.
        
    Raises:
        ProjectNotFoundException: If no cuhkit project file is found at the path.
        ProjectLoadFailureException: If the cuhkit project file could not be loaded.
        
    Returns:
        AddonProject | ModProject: The loaded project.
    """

    if not does_project_exist_at_path(path):
        raise ProjectNotFoundException(path)
    
    file_path = get_project_file_path(path)
    
    with open(file_path, "r") as project_file:
        try:
            json_data = json.loads(project_file.read())
        except json.JSONDecodeError as exception:
            raise ProjectLoadFailureException(f"Failed to load cuhkit project at path (read or JSON decode error): {file_path}") from exception
        
    try:
        raw_project_type = json_data.get("project_type")
        project_type = ProjectType(raw_project_type)
    except ValueError as exception:
        raise ProjectLoadFailureException(f"Failed to load cuhkit project at path (invalid project type, got: {raw_project_type}): {file_path}") from exception

    if project_type == ProjectType.ADDON:
        return AddonProject.from_path(path)
    elif project_type == ProjectType.MOD:
        return ModProject.from_path(path)