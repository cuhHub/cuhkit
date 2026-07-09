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
from unittest.mock import patch, MagicMock

from cuhkit.cli_context import CLIContext

# // Main
def test_cli_context_creation():
    context = CLIContext(project = None, credentials = None)

    assert context.project is None
    assert context.credentials is None

def test_cli_context_with_project():
    mock_project = MagicMock()
    mock_project.name = "test_project"

    context = CLIContext(project = mock_project, credentials = None)

    assert context.project.name == "test_project"