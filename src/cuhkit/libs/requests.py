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
import requests

from cuhkit import __VERSION__
from cuhkit.log import logger

# // Main
USER_AGENT = f"cuhkit/{__VERSION__}"

def request(
    method: str,
    url: str,
    params: dict = None,
    body: dict = None,
    files: dict | list[tuple] = None,
    headers: dict = None
) -> requests.Response:
    """
    Sends a request to the provided URL using the provided method.

    Args:
        method (str): The request method (GET, POST, etc.)
        url (str): The URL to send the request to
        params (dict, optional): The query parameters to pass. Defaults to None.
        body (dict, optional): The request body to pass. Defaults to None.
        files (dict | list[tuple], optional): The files to pass. Defaults to None.
        headers (dict, optional): The headers to pass. Defaults to None.

    Returns:
        requests.Response: The response object.
    """
    
    add_headers = {"User-Agent": USER_AGENT}
    
    if headers is None:
        headers = add_headers
    else:
        headers.update(add_headers)
        
    logger.debug(f"libs/request: Sending request to [{method}] {url} (params: {params}, body: {body}, files: {files}, headers: {headers})")
    
    return requests.request(
        method = method,
        url = url,
        params = params,
        data = body,
        files = files,
        headers = headers
    )
    
def is_plain_text_response(response: requests.Response) -> bool:
    """
    Checks if the response is plain text.

    Args:
        response (requests.Response): The response object.

    Returns:
        bool: True if the response is plain text, False otherwise.
    """

    content_type = response.headers.get("content-type")
    
    if content_type is None:
        return False
    
    return content_type.find("text/plain") != -1