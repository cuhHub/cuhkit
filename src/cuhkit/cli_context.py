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
import click
from dataclasses import dataclass
from typing import Callable
from functools import wraps
from pathlib import Path

from cuhkit import projects
from cuhkit import credentials

# // Main
def pass_context(function: Callable):
    """
    Decorator to pass CLI context to functions.

    Args:
        function (Callable): The function to decorate.
    """

    @wraps(function)
    def wrapper(*args, **kwargs):
        return function(*args, **kwargs, context = get_context())
    
    return wrapper

@dataclass
class CLIContext:
    """
    Context object for the cuhkit CLI.
    """

    project: projects.AddonProject | projects.ModProject | None
    credentials_holder: credentials.CredentialsHolder
    
    def get_credentials(self, use_debug: bool = False) -> credentials.Credentials:
        """
        Returns the credentials, using debug credentials if `use_debug` is True. 

        Args:
            use_debug (bool, optional): Whether or not to use debug credentials. Defaults to False.

        Returns:
            credentials.Credentials: The credentials.
        """

        return self.credentials_holder.get_credentials(credentials.CredentialsType.DEBUG if use_debug else credentials.CredentialsType.NORMAL)
    
def setup_context(context: click.Context):
    """
    Sets up the click context.

    Args:
        context (click.Context): The click context.
    """

    context.ensure_object(dict)

    context.obj["context"] = CLIContext(
        project = projects.load_project_at_path(Path.cwd()) if projects.does_project_exist_at_path(Path.cwd()) else None,
        credentials_holder = credentials.get_credentials_holder()
    )
    
def get_context() -> CLIContext:
    """
    Returns the CLI context.

    Returns:
        CLIContext: The CLI context.
    """

    return click.get_current_context().obj["context"]