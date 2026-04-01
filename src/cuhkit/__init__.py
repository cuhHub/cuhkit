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

# // Main
import sys
from pathlib import Path

__VERSION__ = "1.0.0"
CUHKIT_DATA_PATH = Path.home() / ".cuhkit"
CUHKIT_PACKAGE_PATH = Path(__file__).parent

if getattr(sys, "frozen", False): # pyinstaller context
    CUHKIT_PACKAGE_PATH = Path(sys._MEIPASS) / "cuhkit"

from . import exceptions
from . import log
from . import libs
from . import projects
from . import credentials

from . import cli_context
from .cli import cli