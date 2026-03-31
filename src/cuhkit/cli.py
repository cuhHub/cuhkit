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
from pathlib import Path
from functools import wraps
from typing import Callable

from cuhkit import __VERSION__
from cuhkit import projects
from cuhkit import cli_context
from cuhkit.log import set_logging_verbose, logger

# // Main
def requires_project(project_type: projects.ProjectType | None = None):
    """
    Decorator for click commands that require a cuhkit project.
    
    Args:
        project_type (projects.ProjectType | None): The type of project required, or None to allow any.
    """

    def decorator(function: Callable):
        @wraps(function)
        def wrapper(*args, **kwargs):
            context = cli_context.get_context()

            if context.project is None:
                logger.error("No cuhkit project found in current directory, this command must be run in a cuhkit project directory.")
                return
            
            if project_type is not None and context.project.project_type != project_type:
                logger.error(f"Current cuhkit project is not of required type {project_type}, got {context.project.project_type}.")
                return

            return function(*args, **kwargs, project = context.project)
        
        return wrapper
    
    return decorator

@click.group()
@click.version_option(__VERSION__)
@click.help_option()
@click.option("verbose", "--verbose", "-v", is_flag = True, help = "Enables verbose output.")
@click.pass_context
def cli(context: click.Context, verbose: bool):
    """
    Main CLI entry point.
    """
    
    cli_context.setup_context(context)

    if verbose:
        set_logging_verbose(verbose)

    logger.info("cuhkit - A CLI-oriented Python package for handling cuhHub Stormworks projects (addons/mods).")

@cli.command()
@click.argument(
    "name",
    type = str,
    required = True
)
@click.option(
    "--path", "-p",
    type = click.Path(exists = True, file_okay = False, dir_okay = True, resolve_path = True, path_type = Path),
    default = ".",
    help = "The directory to create the project in."
)
@click.option(
    "--type", "-t", "project_type",
    type = click.Choice(projects.ProjectType),
    required = True,
    help = "The type of the project to create."
)
def new(name: str, path: Path, project_type: projects.ProjectType):
    """
    Create a new cuhkit project.
    """
    
    if projects.does_project_exist_at_path(path):
        logger.error(f"A cuhkit project already exists at {path}.")
        return

    if project_type == projects.ProjectType.ADDON:
        project = projects.create_addon_project(name, path)
    elif project_type == projects.ProjectType.MOD:
        project = projects.create_mod_project(name, path)
        
    project.save()

    logger.info(f"Created cuhkit project at {path}.")

@cli.command()
@cli_context.pass_context
@requires_project()
@click.confirmation_option(prompt = "Are you sure you want to delete this cuhkit project?")
def delete(context: cli_context.CLIContext, project: projects.Project):
    """
    Deletes a cuhkit project.
    """

    project.delete()
    logger.info("Deleted cuhkit project.")

@cli.command()
@cli_context.pass_context
@requires_project(projects.ProjectType.ADDON)
def build(context: cli_context.CLIContext, project: projects.AddonProject):
    """
    Builds and syncs a cuhkit addon project.
    """

    project.build()
    project.sync()
    logger.info("Built cuhkit addon project.")
    
@cli.command()
@cli_context.pass_context
@requires_project(projects.ProjectType.ADDON)
def sync(context: cli_context.CLIContext, project: projects.AddonProject):
    """
    Sync a cuhkit project to Stormworks.
    Note that the 'build' command also does this, but builds beforehand.
    """

    project.sync()
    logger.info("Synced cuhkit addon project.")
    
@cli.command()
@cli_context.pass_context
@requires_project(projects.ProjectType.ADDON)
def setup(context: cli_context.CLIContext, project: projects.AddonProject):
    """
    Sets up a cuhkit project for the first time.
    Should only really be used after cloning an existing addon project.
    """

    project.setup()
    logger.info("Performed setup with cuhkit addon project.")

@cli.command()
@cli_context.pass_context
@requires_project()
def publish(context: cli_context.CLIContext, project: projects.Project):
    """
    Publish a cuhkit project to cuhHub.
    """

    pass