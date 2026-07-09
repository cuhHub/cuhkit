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
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from cuhkit.libs.addon_builder import (
    BuilderMetadata,
    WebImport,
    GitPathImport,
    BuildOptions,
    build_directory,
    build_addon,
    load_metadata,
    does_metadata_exist,
    get_expected_metadata_path,
    handle_content,
    is_path_in_list,
    get_vehicle_files,
    METADATA_FILE_NAME
)

# // Main
def test_metadata_defaults():
    metadata = BuilderMetadata()

    assert metadata.build_order is None
    assert metadata.ignore == []
    assert metadata.import_web == []
    assert metadata.import_local == []
    assert metadata.import_git == []

def test_metadata_with_build_order(temp_dir: Path):
    (temp_dir / "a.lua").write_text("")
    (temp_dir / "b.lua").write_text("")

    metadata = BuilderMetadata(build_order = [Path("b.lua"), Path("a.lua")])

    resolved = metadata.resolve_build_order(temp_dir)
    assert resolved == [temp_dir / "b.lua", temp_dir / "a.lua"]

def test_metadata_resolve_ignores(temp_dir: Path):
    metadata = BuilderMetadata(ignore = [Path("ignore_me.lua")])

    resolved = metadata.resolve_ignores(temp_dir)
    assert resolved == [temp_dir / "ignore_me.lua"]

def test_metadata_handle_paths_with_build_order(temp_dir: Path):
    (temp_dir / "a.lua").write_text("")
    (temp_dir / "b.lua").write_text("")
    (temp_dir / "c.lua").write_text("")

    metadata = BuilderMetadata(build_order = [Path("b.lua"), Path("a.lua")])

    paths = [temp_dir / "a.lua", temp_dir / "b.lua", temp_dir / "c.lua"]
    handled = metadata.handle_paths(temp_dir, paths)

    assert handled[0] == temp_dir / "b.lua"
    assert handled[1] == temp_dir / "a.lua"

def test_metadata_handle_paths_ignores(temp_dir: Path):
    (temp_dir / "keep.lua").write_text("")
    (temp_dir / "ignore.lua").write_text("")

    metadata = BuilderMetadata(ignore = [Path("ignore.lua")])

    paths = [temp_dir / "keep.lua", temp_dir / "ignore.lua"]
    handled = metadata.handle_paths(temp_dir, paths)

    assert temp_dir / "keep.lua" in handled
    assert temp_dir / "ignore.lua" not in handled

def test_metadata_handle_paths_deduplicates(temp_dir: Path):
    (temp_dir / "a.lua").write_text("")

    metadata = BuilderMetadata(build_order = [Path("a.lua"), Path("a.lua")])

    paths = [temp_dir / "a.lua"]
    handled = metadata.handle_paths(temp_dir, paths)

    assert len(handled) == 1

def test_metadata_handle_paths_skips_nonexistent_build_order(temp_dir: Path):
    (temp_dir / "a.lua").write_text("")

    metadata = BuilderMetadata(build_order = [Path("nonexistent.lua"), Path("a.lua")])

    paths = [temp_dir / "a.lua"]
    handled = metadata.handle_paths(temp_dir, paths)

    assert handled == [temp_dir / "a.lua"]

def test_load_metadata_defaults(temp_dir: Path):
    metadata = load_metadata(temp_dir)

    assert metadata.build_order is None
    assert metadata.ignore == []

def test_load_metadata_from_file(temp_dir: Path):
    metadata_path = temp_dir / METADATA_FILE_NAME
    metadata_path.write_text('{"build_order": ["main.lua"]}')

    metadata = load_metadata(temp_dir)
    assert metadata.build_order == [Path("main.lua")]

def test_does_metadata_exist(temp_dir: Path):
    assert does_metadata_exist(temp_dir) is False

    (temp_dir / METADATA_FILE_NAME).write_text("{}")
    assert does_metadata_exist(temp_dir) is True

def test_get_expected_metadata_path(temp_dir: Path):
    expected = temp_dir / METADATA_FILE_NAME
    assert get_expected_metadata_path(temp_dir) == expected

def test_handle_content(temp_dir: Path):
    file_path = temp_dir / "src" / "main.lua"
    content = "print('hello')"

    result = handle_content(temp_dir / "src", file_path, content)
    assert result == "-- cuhkit: main.lua\nprint('hello')"

def test_is_path_in_list(temp_dir: Path):
    path_a = temp_dir / "a.lua"
    path_b = temp_dir / "b.lua"

    path_list = [path_a]
    assert is_path_in_list(path_a, path_list) is True
    assert is_path_in_list(path_b, path_list) is False

def test_get_vehicle_files(temp_dir: Path):
    (temp_dir / "vehicle_1.xml").write_text("")
    (temp_dir / "vehicle_2.xml").write_text("")
    (temp_dir / "main.lua").write_text("")

    vehicles = get_vehicle_files(temp_dir)
    assert len(vehicles) == 2

def test_build_addon_ignores_output_file(temp_dir: Path):
    output = temp_dir / "output.lua"

    (temp_dir / "a.lua").write_text("-- a")
    (temp_dir / "b.lua").write_text("-- b")

    build_addon(temp_dir, output)

    assert output.exists()
    content = output.read_text()
    assert "-- cuhkit:" in content

def test_build_addon_with_ignore_options(temp_dir: Path):
    output = temp_dir / "output.lua"

    (temp_dir / "a.lua").write_text("-- a")
    (temp_dir / "b.lua").write_text("-- b")

    options = BuildOptions(ignore_paths = [temp_dir / "a.lua"])
    build_addon(temp_dir, output, options)

    content = output.read_text()
    assert "-- cuhkit: b.lua" in content
    assert "a.lua" not in content

def test_build_directory_skips_non_lua_files(temp_dir: Path):
    (temp_dir / "main.lua").write_text("-- main")
    (temp_dir / "data.txt").write_text("some data")

    result = build_directory(temp_dir)
    assert len(result) == 1
    assert "-- cuhkit: main.lua" in result[0]

def test_build_directory_recursive(temp_dir: Path):
    sub_dir = temp_dir / "sub"
    sub_dir.mkdir()
    (sub_dir / "nested.lua").write_text("-- nested")

    (temp_dir / "main.lua").write_text("-- main")

    result = build_directory(temp_dir)
    assert len(result) == 2
    assert any("-- cuhkit: main.lua" in line for line in result)
    assert any("nested.lua" in line for line in result)

def test_web_import_model():
    web = WebImport(url = "https://example.com/file.lua", name = "my_import")
    assert web.url == "https://example.com/file.lua"
    assert web.name == "my_import"

def test_git_path_import_model():
    git = GitPathImport(repo_url = "https://github.com/user/repo.git", branch = "main", paths = [Path("libs")])
    assert git.repo_url == "https://github.com/user/repo.git"
    assert git.branch == "main"
    assert git.paths == [Path("libs")]
    assert git.destination == "."

def test_git_path_import_migrates_path_field():
    data = {
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "path": "old_lib"
    }

    result = GitPathImport.model_validate(data)
    assert result.paths == [Path("old_lib")]
    assert not hasattr(result, "path")

def test_git_path_import_migrates_merges_path_and_paths():
    data = {
        "repo_url": "https://github.com/user/repo.git",
        "branch": "main",
        "paths": ["lib_a"],
        "path": "lib_b"
    }

    result = GitPathImport.model_validate(data)
    assert Path("lib_a") in result.paths
    assert Path("lib_b") in result.paths
    assert len(result.paths) == 2