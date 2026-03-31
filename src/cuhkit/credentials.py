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

from enum import Enum
from pathlib import Path

from cuhkit import CUHKIT_DATA_PATH
from cuhkit.log import logger

# // Main
CREDENTIALS_PATH = CUHKIT_DATA_PATH / "credentials.json"

class CredentialsType(Enum):
    """
    Represents the type of credentials.
    """
    
    DEBUG = "debug"
    NORMAL = "normal"

class Credentials(BaseModel):
    """
    Base class for credentials
    """
    
    api_token: UUID4 | None = None
    credentials_type: CredentialsType
    
class NormalCredentials(Credentials):
    """
    Credentials for normal contexts (e.g. publishing to production)
    """
    
    credentials_type: CredentialsType = CredentialsType.NORMAL
    
class DebugCredentials(Credentials):
    """
    Credentials for debug contexts (e.g. local development)
    """
    
    credentials_type: CredentialsType = CredentialsType.DEBUG
    
class CredentialsHolder(BaseModel):
    """
    Model to store credentials of all types.
    """
    
    credentials: dict[CredentialsType, Credentials] = {
        CredentialsType.NORMAL: NormalCredentials(),
        CredentialsType.DEBUG: DebugCredentials()
    }

    path: Path
    
    def get_credentials(self, credentials_type: CredentialsType = CredentialsType.NORMAL) -> Credentials:
        """
        Gets the credentials for the given type.
        
        Args:
            credentials_type (CredentialsType): The type of credentials to get.
        
        Returns:
            Credentials: The credentials for the given type.
        """
        
        return self.credentials[credentials_type]
    
    def save(self):
        """
        Save credentials to the file.
        """
        
        logger.info(f"Saving credentials to {self.path}")
        self.path.write_text(self.model_dump_json(indent = 3))
    
    @classmethod
    def create_new(cls, path: Path):
        """
        Creates a new credentials holder, saving it automatically.
        
        Args:
            path (Path): The path to the credentials file.
        """
        
        credentials_holder = cls(path = path)
        credentials_holder.save()
        
        return credentials_holder
    
    @classmethod
    def try_load(cls, path: Path) -> CredentialsHolder:
        """
        Loads credentials from the file, or creating new and saving if it doesn't exist.
        
        Args:
            path (Path): The path to the credentials file.
        
        Returns:
            CredentialsHolder: The loaded credentials.
        """
        
        if not path.exists():
            logger.warning(f"No credentials found at {path}. Creating new.")
            return cls.create_new(path)
        
        logger.debug(f"Getting credentials from: {path}")
        
        content = path.read_text()
        return cls.model_validate_json(content)
    
def get_credentials_holder() -> CredentialsHolder:
    """
    Loads credentials from a file.
    
    Returns:
        CredentialsHolder: The loaded credentials.
    """
    
    CREDENTIALS_PATH.parent.mkdir(parents = True, exist_ok = True)
    return CredentialsHolder.try_load(CREDENTIALS_PATH)

def remove_credentials():
    """
    Removes the credentials file.
    """
    
    CREDENTIALS_PATH.unlink(missing_ok = True)