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
from unittest.mock import patch, MagicMock
from pathlib import Path

from cuhkit.libs.api import Client, APIException

# // Main
@pytest.fixture
def client():
    return Client(token = "test-token-123")

def test_client_initialization(client: Client):
    assert client.token == "test-token-123"

def test_get_url(client: Client):
    url = client.get_url("/servers")
    assert url == "https://api.cuhhub.com/servers"

def test_get_url_strips_leading_slash(client: Client):
    url = client.get_url("servers")
    assert url == "https://api.cuhhub.com/servers"

def test_send_request_success(client: Client):
    with patch("cuhkit.libs.api.requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.json.return_value = {"id": 1, "name": "test"}
        mock_request.return_value = mock_response

        result = client.send_request("GET", "/servers")

        assert result == {"id": 1, "name": "test"}

        args, kwargs = mock_request.call_args
        assert kwargs["headers"]["x-authorization"] == "Bearer test-token-123"

def test_send_request_raises_on_bad_status(client: Client):
    with patch("cuhkit.libs.api.requests.request") as mock_request:
        mock_response = MagicMock()
        mock_response.ok = False
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_request.return_value = mock_response

        with pytest.raises(APIException):
            client.send_request("GET", "/servers")

def test_send_request_raises_on_network_error(client: Client):
    with patch("cuhkit.libs.api.requests.request") as mock_request:
        mock_request.side_effect = requests.exceptions.RequestException("Connection refused")

        with pytest.raises(APIException):
            client.send_request("GET", "/servers")

def test_get_servers(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = [{"id": 1}]

        result = client.get_servers()
        assert result == [{"id": 1}]
        mock_send.assert_called_with("GET", "/servers")

def test_get_server(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = {"id": 1}

        result = client.get_server(1)
        assert result == {"id": 1}
        mock_send.assert_called_with("GET", "/servers/1")

def test_refresh_server(client: Client):
    with patch.object(client, "send_request") as mock_send:
        client.refresh_server(1)
        mock_send.assert_called_with("POST", "/servers/1/refresh")

def test_get_addons(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = ["addon1", "addon2"]

        result = client.get_addons()
        assert result == ["addon1", "addon2"]
        mock_send.assert_called_with("GET", "/storage/addons")

def test_get_mods(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = ["mod1", "mod2"]

        result = client.get_mods()
        assert result == ["mod1", "mod2"]
        mock_send.assert_called_with("GET", "/storage/mods")

def test_is_addon_in_server(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = {"addons": ["addon1", "addon2"]}

        assert client.is_addon_in_server("addon1", 1) is True
        assert client.is_addon_in_server("addon3", 1) is False

def test_is_mod_in_server(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = {"mods": ["mod1", "mod2"]}

        assert client.is_mod_in_server("mod1", 1) is True
        assert client.is_mod_in_server("mod3", 1) is False

def test_does_addon_exist(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = ["addon1", "addon2"]

        assert client.does_addon_exist("addon1") is True
        assert client.does_addon_exist("addon3") is False

def test_does_mod_exist(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = ["mod1", "mod2"]

        assert client.does_mod_exist("mod1") is True
        assert client.does_mod_exist("mod3") is False

def test_add_addon(client: Client):
    with patch.object(client, "send_request") as mock_send:
        client.add_addon("my_addon", 1)
        mock_send.assert_called_with(
            method = "PATCH",
            endpoint = "/servers/1/addons",
            body = {"addon_name": "my_addon"}
        )

def test_add_mod(client: Client):
    with patch.object(client, "send_request") as mock_send:
        client.add_mod("my_mod", 1)
        mock_send.assert_called_with(
            method = "PATCH",
            endpoint = "/servers/1/mods",
            body = {"mod_name": "my_mod"}
        )

def test_upload_addon_uses_post_when_not_exists(client: Client, temp_dir: Path):
    script = temp_dir / "script.lua"
    script.write_text("-- code")
    playlist = temp_dir / "playlist.xml"
    playlist.write_text("<playlist></playlist>")

    with patch.object(client, "does_addon_exist", return_value = False):
        with patch.object(client, "send_request") as mock_send:
            client.upload_addon("my_addon", script, playlist)

            args, kwargs = mock_send.call_args
            assert kwargs["method"] == "POST"

def test_upload_addon_uses_patch_when_exists(client: Client, temp_dir: Path):
    script = temp_dir / "script.lua"
    script.write_text("-- code")
    playlist = temp_dir / "playlist.xml"
    playlist.write_text("<playlist></playlist>")

    with patch.object(client, "does_addon_exist", return_value = True):
        with patch.object(client, "send_request") as mock_send:
            client.upload_addon("my_addon", script, playlist)

            args, kwargs = mock_send.call_args
            assert kwargs["method"] == "PATCH"

def test_upload_mod_uses_post_when_not_exists(client: Client, temp_dir: Path):
    mod_zip = temp_dir / "mod.zip"
    mod_zip.write_text("zip data")

    with patch.object(client, "does_mod_exist", return_value = False):
        with patch.object(client, "send_request") as mock_send:
            client.upload_mod("my_mod", mod_zip)

            args, kwargs = mock_send.call_args
            assert kwargs["method"] == "POST"

def test_upload_mod_uses_patch_when_exists(client: Client, temp_dir: Path):
    mod_zip = temp_dir / "mod.zip"
    mod_zip.write_text("zip data")

    with patch.object(client, "does_mod_exist", return_value = True):
        with patch.object(client, "send_request") as mock_send:
            client.upload_mod("my_mod", mod_zip)

            args, kwargs = mock_send.call_args
            assert kwargs["method"] == "PATCH"

def test_get_persistent_data_returns_none_on_error(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.side_effect = APIException("Not found")

        result = client.get_persistent_data("some_key")
        assert result is None

def test_get_persistent_data_success(client: Client):
    with patch.object(client, "send_request") as mock_send:
        mock_send.return_value = {"key": "some_key", "value": "some_value"}

        result = client.get_persistent_data("some_key")
        assert result == {"key": "some_key", "value": "some_value"}

def test_resolve_file_for_request(client: Client, temp_dir: Path):
    file_path = temp_dir / "test.lua"
    file_path.write_text("-- content")

    name, file_obj = client._resolve_file_for_request("script_file", file_path)
    assert name == "script_file"
    assert file_obj.read() == b"-- content"
    file_obj.close()