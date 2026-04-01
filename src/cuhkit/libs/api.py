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

# TODO: might be worth creating a separate package for this in the future
#       so many endpoints and responses to cover though, so this won't be a priority

# // Imports
import requests
from pathlib import Path

from typing import Any

# // Main
class APIException(Exception):
    """
    Exception class for API errors.
    """

    pass

class Client():
    """
    A client for the cuhHub API.
    """
    
    CUHHUB_API_URL = "https://api.cuhhub.com"
    
    def __init__(self, token: str):
        """
        Initializes Client instances.
        
        Args:
            token (str): The API token to use.
        """
        
        self.token = token
        
    def _resolve_file_for_request(self, name: str, file: Path) -> tuple[str, Any]:
        """
        Resolves a file for a request.

        Args:
            name (str): The name of the file for the request (doesn't have to be the file name).
            file (Path): The file to resolve.

        Returns:
            tuple[str, Any]: The name and file content for a request.
        """
        
        return (name, file.open("rb"))
        
    def get_url(self, endpoint: str) -> str:
        """
        Returns the URL for a given endpoint.

        Args:
            endpoint (str): The endpoint to get the URL for.

        Returns:
            str: The URL.
        """
        
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        
        return f"{self.CUHHUB_API_URL}/{endpoint}"

    def send_request(
        self,
        method: str,
        endpoint: str,
        params: dict = None,
        body: dict = None,
        files: dict | list[tuple] = None
    ) -> dict:
        """
        Sends a request to the cuhHub API.

        Args:
            method (str): The request method (GET, POST, etc.)
            endpoint (str): The API endpoint to send a request to (e.g. /servers)
            params (dict, optional): The query parameters to pass. Defaults to None.
            body (dict, optional): The request body to pass. Defaults to None.
            files (dict | list[tuple], optional): The files to pass. Defaults to None.
            
        Raises:
            APIException: If the request fails.

        Returns:
            dict: The JSON response.
        """        
        
        try:
            response = requests.request(
                method = method,
                url = self.get_url(endpoint),
                params = params,
                json = body,
                files = files,
                headers = {
                    "x-authorization": f"Bearer {self.token}"
                }
            )
        except requests.exceptions.RequestException as exception:
            raise APIException(f"Failed to send request: {exception}") from exception
        
        if not response.ok:
            raise APIException(f"Response not ok, got: {response.status_code} {response.text}")
        
        return response.json()
    
    def get_servers(self) -> list[dict]:
        """
        Returns all servers from the cuhHub API.

        Returns:
            list[dict]: The returned servers.
        """
        
        return self.send_request("GET", "/servers")
    
    def get_server(self, server_id: int) -> dict:
        """
        Returns a server from the cuhHub API.

        Args:
            server_id (int): The ID of the server to get.

        Returns:
            dict: The server.
        """
        
        return self.send_request("GET", f"/servers/{server_id}")
    
    def refresh_server(self, server_id: int):
        """
        Refreshes a cuhHub server.

        Args:
            server_id (int): The ID of the server to refresh.
        """
        
        self.send_request("POST", f"/servers/{server_id}/refresh")
    
    def get_addons(self) -> list[str]:
        """
        Returns all cuhHub addons.

        Returns:
            list[str]: The JSON response.
        """
        
        return self.send_request("GET", "/storage/addons")
    
    def get_mods(self) -> list[str]:
        """
        Returns all cuhHub mods.

        Returns:
            list[str]: The JSON response.
        """
        
        return self.send_request("GET", "/storage/mods")
    
    def is_addon_in_server(self, addon_name: str, server_id: int) -> bool:
        """
        Checks if an addon is in a cuhHub server.

        Args:
            addon_name (str): The name of the addon to check.
            server_id (int): The ID of the server to check.

        Returns:
            bool: True if the addon is in the server, False otherwise.
        """
        
        return addon_name in self.get_server(server_id)["addons"]
    
    def is_mod_in_server(self, mod_name: str, server_id: int) -> bool:
        """
        Checks if a mod is in a cuhHub server.

        Args:
            mod_name (str): The name of the mod to check.
            server_id (int): The ID of the server to check.

        Returns:
            bool: True if the mod is in the server, False otherwise.
        """
        
        return mod_name in self.get_server(server_id)["mods"]
    
    def does_addon_exist(self, addon_name: str) -> bool:
        """
        Checks if an addon exists.

        Args:
            addon_name (str): The name of the addon to check.

        Returns:
            bool: True if the addon exists, False otherwise.
        """
        
        return addon_name in self.get_addons()
    
    def does_mod_exist(self, mod_name: str) -> bool:
        """
        Checks if a mod exists.

        Args:
            mod_name (str): The name of the mod to check.

        Returns:
            bool: True if the mod exists, False otherwise.
        """
        
        return mod_name in self.get_mods()
    
    def add_addon(self, addon_name: str, server_id: int):
        """
        Adds an addon to a cuhHub server.

        Args:
            addon_name (str): The name of the addon to add.
            server_id (int): The ID of the server to add the addon to.
        """
        
        self.send_request(
            method = "PATCH",
            endpoint = f"/servers/{server_id}/addons",
            body = {
                "addon_name" : addon_name
            }
        )
        
    def add_mod(self, mod_name: str, server_id: int):
        """
        Adds a mod to a cuhHub server.

        Args:
            mod_name (str): The name of the mod to add.
            server_id (int): The ID of the server to add the mod to.
        """
        
        self.send_request(
            method = "PATCH",
            endpoint = f"/servers/{server_id}/mods",
            body = {
                "mod_name" : mod_name
            }
        )
        
    def upload_addon(self, addon_name: str, script_file: Path, playlist_file: Path, vehicle_files: list[Path] = None, *, allow_update: bool = True):
        """
        Uploads an addon.

        Args:
            addon_name (str): The name of the addon.
            script_file (Path): The addon's script.lua file.
            playlist_file (Path): The addon's playlist.xml file.
            vehicle_files (list[Path], optional): The vehicle files in the addon, if any. Defaults to None.
            allow_update (bool, optional): Whether or not to allow updating instead of uploading if the addon already exists. Defaults to True.
        """
        
        if vehicle_files is None:
            vehicle_files = []
        
        self.send_request(
            method = "PATCH" if self.does_addon_exist(addon_name) and allow_update else "POST",
            endpoint = f"/storage/addons/{addon_name}",
            files = [
                self._resolve_file_for_request("script_file", script_file),
                self._resolve_file_for_request("playlist_file", playlist_file),
                *[
                    self._resolve_file_for_request("vehicle_files", vehicle_file)
                    for vehicle_file in vehicle_files
                ]
            ]
        )
        
    def upload_mod(self, mod_name: str, mod_zip: Path, *, allow_update: bool = True):
        """
        Uploads a mod.

        Args:
            mod_name (str): The name of the mod.
            mod_zip (Path): The mod's .zip file.
            allow_update (bool, optional): Whether or not to allow updating instead of uploading if the mod already exists. Defaults to True.
        """
        
        self.send_request(
            method = "PATCH" if self.does_mod_exist(mod_name) and allow_update else "POST",
            endpoint = f"/storage/mods/{mod_name}",
            files = [
                self._resolve_file_for_request("mod_zip", mod_zip)
            ]
        )
        
    def get_persistent_data(self, key: str) -> dict | None:
        """
        Returns the persistent data at a key from the cuhHub API.

        Args:
            key (str): The key to get the persistent data for.

        Returns:
            dict | None: The JSON response, or None if data not found or API error.
        """
        
        try:
            return self.send_request("GET", f"/persistent-data/{key}")
        except APIException:
            return None