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
from dataclasses import dataclass
from pathlib import Path

from cuhkit.libs.requests import (
    request,
    requests,
    is_plain_text_response
)

from cuhkit.log import logger

# // Main
class BadTemplateDownload(Exception):
    """
    Exception raised if template download request fails (bad response, etc.)
    """
    
    pass

@dataclass(frozen = True)
class TemplateDownload:
    url: str
    destination: Path
    
    def request_text(self) -> str:
        """
        Sends a request to the URL and returns the text.
        
        Raises:
            BadTemplateDownload: If the request fails, or returns bad content type.

        Returns:
            str: The text of the request.
        """
        
        logger.debug(f"libs/templates: Downloading template at URL {self.url} for path {self.destination}")
        
        try:
            response = request("GET", self.url)
            response.raise_for_status()
        except requests.exceptions.RequestException as exception:
            raise BadTemplateDownload(f"Failed to download template file at URL: {self.url} (request error, exception: {exception})") from exception
        except requests.exceptions.HTTPError as exception:
            raise BadTemplateDownload(f"Failed to download template at file URL: {self.url} (HTTP error (bad status code of {response.status_code}), exception: {exception})") from exception

        if not is_plain_text_response(response):
            raise BadTemplateDownload(f"Failed to download template at file URL: {self.url} (content type is not text/plain, got: {response.headers.get("content-type")})")
        
        return response.text

    def download(self):
        """
        Downloads the template file.
        """
        
        self.destination.write_text(self.request_text())

def copy_template(template_path: Path, downloads: list[TemplateDownload], destination: Path):
    """
    Copy the template to the destination directory.
    
    Args:
        template_path (Path): The path to the template directory.
        downloads (list[TemplateDownload]): A list of downloads to copy over to destination.
        destination (Path): The path to the destination directory.
    """

    logger.info(f"Copying template from {template_path} to {destination}")
    shutil.copytree(template_path, destination, dirs_exist_ok = True)
    
    for download in downloads:
        download.download() # splendid naming