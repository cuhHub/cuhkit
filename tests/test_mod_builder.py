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
import zipfile
from unittest.mock import patch

from cuhkit.libs.mod_builder import build_mod, sync_mod

# // Main
def test_build_mod_creates_zip(temp_dir: Path):
    mod_dir = temp_dir / "mod"
    mod_dir.mkdir()
    (mod_dir / "mod.xml").write_text("<mod></mod>")
    (mod_dir / "mesh.mesh").write_text("mesh data")

    destination = temp_dir / "output" / "mod.zip"

    build_mod(mod_dir, destination)

    assert destination.exists()

    with zipfile.ZipFile(destination, "r") as zf:
        names = zf.namelist()
        assert "mod.xml" in names
        assert "mesh.mesh" in names

def test_build_mod_creates_parent_directories(temp_dir: Path):
    mod_dir = temp_dir / "mod"
    mod_dir.mkdir()
    (mod_dir / "mod.xml").write_text("<mod></mod>")

    destination = temp_dir / "deep" / "nested" / "output.zip"

    build_mod(mod_dir, destination)
    assert destination.exists()

def test_sync_mod_copies_all_files(temp_dir: Path):
    mod_dir = temp_dir / "mod"
    mod_dir.mkdir()
    (mod_dir / "mod.xml").write_text("<mod></mod>")
    (mod_dir / "mesh.mesh").write_text("data")

    stormworks_dir = temp_dir / "stormworks"

    sync_mod(mod_dir, stormworks_dir)

    assert (stormworks_dir / "mod.xml").exists()
    assert (stormworks_dir / "mesh.mesh").exists()

def test_sync_mod_overwrites_existing(temp_dir: Path):
    mod_dir = temp_dir / "mod"
    mod_dir.mkdir()
    (mod_dir / "mod.xml").write_text("new content")

    stormworks_dir = temp_dir / "stormworks"
    stormworks_dir.mkdir()
    (stormworks_dir / "mod.xml").write_text("old content")

    sync_mod(mod_dir, stormworks_dir)

    assert (stormworks_dir / "mod.xml").read_text() == "new content"