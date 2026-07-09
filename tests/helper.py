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
from pathlib import Path
import shutil

# // Main
def get_dump_dir() -> Path:
    """
    Returns the path to the test dump directory.
    Uses script-relative paths, not CWD.
    """

    tests_dir = Path(__file__).parent
    dump_dir = tests_dir / "dump"
    dump_dir.mkdir(parents = True, exist_ok = True)

    return dump_dir

def cleanup_dump_dir():
    """
    Cleans up the dump directory by removing all contents.
    """

    dump_dir = get_dump_dir()

    if dump_dir.exists():
        shutil.rmtree(dump_dir)
        dump_dir.mkdir(parents = True, exist_ok = True)