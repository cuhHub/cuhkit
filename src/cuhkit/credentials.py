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
from pydantic import (
    BaseModel,
    UUID4
)

from pathlib import Path

from cuhkit import CUHKIT_DATA_PATH
from cuhkit.log import logger

# // Main
CREDENTIALS_PATH = CUHKIT_DATA_PATH / "credentials.json"

class Credentials(BaseModel):
    """
    Base class for credentials
    """
    
    api_token: UUID4 | None = None
    path: Path

    def save(self):
        """
        Save the credentials.
        """
        
        logger.info(f"Saving credentials to {self.path}")
        self.path.write_text(self.model_dump_json(indent = 3))
        
    def remove(self):
        """
        Remove the credentials.
        """
        
        logger.info(f"Removing credentials from {self.path}")
        self.path.unlink()
    
    @classmethod
    def create_new(cls, path: Path):
        """
        Creates new credentials, saving it automatically.
        
        Args:
            path (Path): The path to the credentials file.
        """
        
        credentials = cls(path = path)
        credentials.save()
        
        return credentials
    
    @classmethod
    def try_load(cls, path: Path) -> Credentials:
        """
        Loads credentials from the file, or creating new and saving if it doesn't exist.
        
        Args:
            path (Path): The path to the credentials file.
        
        Returns:
            Credentials: The loaded credentials.
        """
        
        if not path.exists():
            logger.warning(f"No credentials found at {path}. Creating new.")
            return cls.create_new(path)
        
        logger.debug(f"Getting credentials from: {path}")
        
        content = path.read_text()
        return cls.model_validate_json(content)
    
def get_credentials() -> Credentials:
    """
    Loads credentials from a file.
    
    Returns:
        Credentials: The loaded credentials.
    """
    
    CREDENTIALS_PATH.parent.mkdir(parents = True, exist_ok = True)
    return Credentials.try_load(CREDENTIALS_PATH)

credentials = get_credentials()