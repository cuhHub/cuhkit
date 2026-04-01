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

from cuhkit.log import logger

# // Main
def build_mod(mod_path: Path, destination_path: Path):
    """
    Builds a mod into an archive ready for publishing.

    Args:
        mod_path (Path): The path to the mod.
        destination_path (Path): The path for the archive.
    """
    
    logger.info("mod_builder: Creating .zip archive for mod")
    archive = Path(shutil.make_archive(destination_path, "zip", mod_path))
    
    logger.info("mod_builder: Moving created archive to destination")
    destination_path.parent.mkdir(parents = True, exist_ok = True)
    shutil.move(archive, destination_path)

def sync_mod(mod_path: Path, stormworks_mod_path: Path):
    """
    Syncs the mod to the game.

    Args:
        mod_path (Path): The path to the mod (where mod.xml is located).
        stormworks_mod_path (Path): The path to the Stormworks mod location.
    """
    
    shutil.copytree(mod_path, stormworks_mod_path, dirs_exist_ok = True)