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

from cuhkit import __version__
from cuhkit import projects
from cuhkit import cli_context

from cuhkit.libs.addon_builder import BuildOptions

from cuhkit.log import set_logging_verbose, logger

from cuhkit.exceptions import CredentialsException

from cuhkit.projects import POSITION_PERSISTENT_DATA_KEY

# // Main
def requires_project(project_types: list[projects.ProjectType] | None = None):
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
            
            if project_types is not None and context.project.project_type not in project_types:
                logger.error(f"This command is not compatible with this cuhkit project. Current cuhkit project is not any of required types {project_types}, got {context.project.project_type}.")
                return

            return function(*args, **kwargs, project = context.project)
        
        return wrapper
    
    return decorator

@click.group()
@click.version_option(__version__)
@click.help_option("--help", "-h")
@click.pass_context
@click.option("verbose", "--verbose", "-v", is_flag = True, help = "Enables verbose logging.")
def cli(context: click.Context, verbose: bool):
    """
    cuhkit - A CLI-oriented Python package for handling cuhHub Stormworks projects (addons/mods).
    """
    
    logger.info("cuhkit - A CLI-oriented Python package for handling cuhHub Stormworks projects (addons/mods).")
    
    cli_context.setup_context(context)

    if verbose:
        set_logging_verbose(verbose)

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
    type = click.Choice(projects.ProjectType, case_sensitive = False),
    required = True,
    help = "The type of the project to create."
)
@click.option(
    "--skip-first-time-setup", "-sfts", "skip_first_time_setup",
    is_flag = True,
    help = "Whether or not to skip the first-time setup process (e.g. copying template files)."
)
def new(name: str, path: Path, project_type: projects.ProjectType, skip_first_time_setup: bool):
    """
    Create a new cuhkit project.
    """
    
    path = path.relative_to(Path.cwd())
    
    if projects.does_project_exist_at_path(path):
        logger.error(f"A cuhkit project already exists at {path}.")
        return

    if project_type == projects.ProjectType.ADDON:
        project = projects.create_addon_project(name, path)
    elif project_type == projects.ProjectType.MOD:
        project = projects.create_mod_project(name, path)

    if not skip_first_time_setup:
        logger.info("Running first-time setup...")
        project.first_time_setup() 
    else:
        logger.info("Skipping first-time setup...")

    logger.info("Saving cuhkit project...")
    project.save()

    logger.info(f"Created cuhkit project at {path}.")

@cli.command()
@cli_context.pass_context
@requires_project()
@click.confirmation_option(prompt = "Are you sure you want to delete this cuhkit project? Only the project file will be deleted. Any files you created will remain.")
def delete(context: cli_context.CLIContext, project: projects.Project):
    """
    Deletes a cuhkit project.
    """

    project.delete()
    logger.info("Deleted cuhkit project.")

@cli.command()
@cli_context.pass_context
@requires_project([projects.ProjectType.ADDON, projects.ProjectType.MOD])
@click.option(
    "--ignore-local-imports", "-ili", "ignore_local_imports",
    is_flag = True,
    help = "Whether or not to ignore local imports in build metadata files (addon only).",
    default = False
)
@click.option(
    "--ignore-web-imports", "-iwi", "ignore_web_imports",
    is_flag = True,
    help = "Whether or not to ignore web imports in build metadata files (addon only).",
    default = False
)
@click.option(
    "--ignore-git-imports", "-igi", "ignore_git_imports",
    is_flag = True,
    help = "Whether or not to ignore git imports in build metadata files (addon only).",
    default = False
)
def build(
    context: cli_context.CLIContext,
    project: projects.AddonProject | projects.ModProject,
    ignore_local_imports: bool,
    ignore_web_imports: bool,
    ignore_git_imports: bool
):
    """
    Builds and syncs a cuhkit project.
    """

    if isinstance(project, projects.AddonProject):
        build_options = BuildOptions(
            ignore_local_imports = ignore_local_imports,
            ignore_web_imports = ignore_web_imports,
            ignore_git_imports = ignore_git_imports
        )

        project.build(build_options)
    elif isinstance(project, projects.ModProject):
        project.build()

    project.sync()
    logger.info("Build complete.")
    
@cli.command()
@cli_context.pass_context
@requires_project([projects.ProjectType.ADDON, projects.ProjectType.MOD])
def sync(context: cli_context.CLIContext, project: projects.AddonProject | projects.ModProject):
    """
    Sync a cuhkit project to Stormworks.
    Note that the 'build' command also does this, but builds beforehand.
    """

    project.sync()
    logger.info("Sync complete.")
    
@cli.command()
@cli_context.pass_context
@requires_project([projects.ProjectType.ADDON])
def get_position(context: cli_context.CLIContext, project: projects.AddonProject):
    """
    Returns the last saved in-game position.
    To use this, save a formatted matrix position to `_debug_pos` (key might be outdated, see source code) via cuhHub persistent data service.
    """

    position = project.get_position()
    
    if position is None:
        logger.error(f"No position found. Save a formatted position to '{POSITION_PERSISTENT_DATA_KEY}' to cuhHub persistent data service via an addon.")
        return
    
    logger.info(f"Position: {position} (copied to clipboard)")
    
@cli.command()
@cli_context.pass_context
@requires_project([projects.ProjectType.ADDON])
def setup(context: cli_context.CLIContext, project: projects.AddonProject):
    """
    Sets up a cuhkit addon project for the first time.
    Should only really be used after cloning an existing addon project.
    """

    project.setup()
    logger.info("Addon project setup complete.")

@cli.command()
@cli_context.pass_context
@requires_project([projects.ProjectType.ADDON, projects.ProjectType.MOD])
@click.option(
    "--server", "-s", "server_id",
    type = int,
    required = True,
    help = "The ID of the server to publish to, or -1 for all servers."
)
@click.option(
    "--dev", "-d", "is_dev",
    is_flag = True,
    help = "Whether or not to publish as a development build."
)
@click.confirmation_option(prompt = "Are you sure you want to publish this cuhkit project?")
def publish(context: cli_context.CLIContext, project: projects.AddonProject | projects.ModProject, server_id: int, is_dev: bool):
    """
    Publish a cuhkit project to cuhHub.
    """
    
    if isinstance(project, projects.AddonProject):
        try:
            project.publish(server_id, is_dev)
            logger.info("Published cuhkit addon project.")
        except CredentialsException:
            logger.error("No API token found in credentials. Please set one using the `set-api-token` command.")
        except FileNotFoundError:
            logger.error("Missing `playlist.xml` file in addon project directory. Try building the addon or running first-time setup. If neither work, please manually create one.")
    elif isinstance(project, projects.ModProject):
        try:
            project.publish(server_id, is_dev)
            logger.info("Published cuhkit mod project.")
        except CredentialsException:
            logger.error("No API token found in credentials. Please set one using the `set-api-token` command.")

@cli.command()
@cli_context.pass_context
@click.argument(
    "api_token",
    type = click.UUID,
    required = True
)
def set_api_token(context: cli_context.CLIContext, api_token: str):
    """
    Sets the cuhHub API token in credentials.
    """

    context.credentials.api_token = api_token
    context.credentials.save()
    
@cli.command()
@cli_context.pass_context
@click.confirmation_option(prompt = "Are you sure you want to delete your cuhkit credentials (API token, etc.)?")
def delete_credentials(context: cli_context.CLIContext):
    """
    Deletes cuhkit credentials.
    """

    context.credentials.remove()
    logger.info("Deleted cuhkit credentials.")
    
if __name__ == "__main__":
    cli()