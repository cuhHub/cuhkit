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
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock

from cuhkit.libs.templates import (
    TemplateDownload,
    copy_template,
    BadTemplateDownload
)

# // Main
def test_template_download_request_text_success():
    with patch("cuhkit.libs.templates.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "file content"
        mock_response.headers = {"content-type": "text/plain"}
        mock_request.return_value = mock_response

        download = TemplateDownload(url = "https://example.com/file.lua", destination = Path("/tmp/file.lua"))
        text = download.request_text()

        assert text == "file content"

def test_template_download_request_text_raises_on_bad_content_type():
    with patch("cuhkit.libs.templates.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "{}"
        mock_response.headers = {"content-type": "application/json"}
        mock_request.return_value = mock_response

        download = TemplateDownload(url = "https://example.com/file.lua", destination = Path("/tmp/file.lua"))

        with pytest.raises(BadTemplateDownload):
            download.request_text()

def test_template_download_request_text_raises_on_http_error():
    with patch("cuhkit.libs.templates.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.headers = {"content-type": "text/plain"}
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("HTTP Error")
        mock_request.return_value = mock_response

        download = TemplateDownload(url = "https://example.com/file.lua", destination = Path("/tmp/file.lua"))

        with pytest.raises(BadTemplateDownload):
            download.request_text()

def test_template_download_writes_file(temp_dir: Path):
    with patch("cuhkit.libs.templates.request") as mock_request:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "downloaded content"
        mock_response.headers = {"content-type": "text/plain"}
        mock_request.return_value = mock_response

        destination = temp_dir / "downloaded.lua"
        download = TemplateDownload(url = "https://example.com/file.lua", destination = destination)
        download.download()

        assert destination.exists()
        assert destination.read_text() == "downloaded content"

def test_copy_template_copies_directory(temp_dir: Path):
    template_dir = temp_dir / "template"
    template_dir.mkdir()
    (template_dir / "main.lua").write_text("-- template main")
    (template_dir / "lib.lua").write_text("-- template lib")

    destination = temp_dir / "project"

    with patch("cuhkit.libs.templates.TemplateDownload.download") as mock_download:
        copy_template(template_dir, [], destination)

    assert (destination / "main.lua").exists()
    assert (destination / "lib.lua").exists()
    assert (destination / "main.lua").read_text() == "-- template main"

def test_copy_template_with_downloads(temp_dir: Path):
    template_dir = temp_dir / "template"
    template_dir.mkdir()
    (template_dir / "main.lua").write_text("-- template main")

    destination = temp_dir / "project"

    download = TemplateDownload(url = "https://example.com/intellisense.lua", destination = destination / "intellisense.lua")

    with patch("cuhkit.libs.templates.TemplateDownload.download") as mock_download:
        copy_template(template_dir, [download], destination)

    mock_download.assert_called_once()
    assert (destination / "main.lua").exists()