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

from cuhkit import (
    __VERSION__
)

from cuhkit.projects import (
    ProjectType,
    does_project_exist_at_path,
    create_addon_project,
    create_mod_project
)

from cuhkit.log import set_logging_verbose

# // Main

@click.group()
@click.version_option(__VERSION__)
@click.help_option()
@click.option("verbose", "--verbose", "-v", is_flag = True, help = "Enables verbose output.")
def cli(verbose: bool):
    """
    Main CLI entry point.
    """

    if verbose:
        set_logging_verbose(verbose)

    click.echo("cuhkit - A CLI-oriented Python package for handling cuhHub Stormworks projects (addons/mods).")

@cli.command()
@click.argument(
    "name",
    type = str,
    required = True
)
@click.option(
    "--path", "-p",
    type = click.Path(exists = True, file_okay = False, dir_okay = True, resolve_path = True),
    default = ".",
    help = "The directory to create the project in."
)
@click.option(
    "--type", "-t", "project_type",
    type = click.Choice(ProjectType),
    required = True,
    help = "The type of the project to create."
)
def new(name: str, path: str, project_type: ProjectType):
    """
    Create a new cuhkit project.
    """
    
    if does_project_exist_at_path(path):
        click.echo(f"A cuhkit project already exists at {path}.", err = True)
        return

    if project_type == ProjectType.ADDON:
        create_addon_project(name, path)
    elif project_type == ProjectType.MOD:
        create_mod_project(name, path)
        
    click.echo(f"Created cuhkit project at {path}.")

@cli.command()
def clean():
    """
    Cleans a cuhkit project.
    """

    pass

@cli.command()
def build():
    """
    Build a cuhkit project.
    """

    pass

@cli.command()
def publish():
    """
    Publish a cuhkit project to cuhHub.
    """

    pass