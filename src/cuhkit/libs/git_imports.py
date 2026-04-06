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
from git import Repo
from pathlib import Path
import shutil
import tempfile

from cuhkit.log import logger

# // Main
def import_path_in_repo(repo_url: str, branch: str, path: Path, destination: Path):
    """
    Imports a folder/file from a git repo.

    Args:
        repo_url (str): The URL of the git repo.
        branch (str): The branch to use.
        path (Path): The path of the file/folder in the repo
        destination (Path): The path to import the file/folder to.
        
    Raises:
        FileNotFoundError: If the path does not exist in the repo.
    """
    
    with tempfile.TemporaryDirectory(suffix = "_git_import_temp_repo") as temp_repo_path:
        logger.debug(f"git_import: Cloning repo ({repo_url}, branch: {branch}) to temp dir: {temp_repo_path}")
        
        repo = Repo.clone_from(
            repo_url,
            temp_repo_path,
            depth = 1,
            no_checkout = True,
            filter = "blob:none",
            branch = branch
        )

        repo.git.sparse_checkout("init", "--cone")
        repo.git.sparse_checkout("set", str(path))
        repo.git.checkout("HEAD")
        
        src = temp_repo_path / path
        
        if not src.exists():
            raise FileNotFoundError(f"Path does not exist in repo: {src}")
        
        destination.mkdir(parents = True, exist_ok = True)

        logger.debug(f"git_import: Copying {src} to {destination}")

        if src.is_dir():
            shutil.copytree(src, destination, dirs_exist_ok = True)
        else:
            shutil.copy2(src, destination)