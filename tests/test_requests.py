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

from unittest.mock import patch, Mock

from cuhkit.libs.requests import (
    request,
    is_plain_text_response,
    USER_AGENT
)

# // Main
class MockResponse:
    def __init__(self, status_code = 200, content = "", headers = None):
        self.status_code = status_code
        self._content = content
        self.headers = headers or {}
        self.text = content

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

def test_request_sets_user_agent():
    with patch("cuhkit.libs.requests.requests.request") as mock_request:
        mock_request.return_value = MockResponse()

        request("GET", "https://example.com")

        args, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "https://example.com"
        assert kwargs["headers"]["User-Agent"] == USER_AGENT

def test_request_passes_params():
    with patch("cuhkit.libs.requests.requests.request") as mock_request:
        mock_request.return_value = MockResponse()

        request("GET", "https://example.com", params = {"key": "value"})

        args, kwargs = mock_request.call_args
        assert kwargs["params"] == {"key": "value"}

def test_request_passes_body():
    with patch("cuhkit.libs.requests.requests.request") as mock_request:
        mock_request.return_value = MockResponse()

        request("POST", "https://example.com", body = {"data": "test"})

        args, kwargs = mock_request.call_args
        assert kwargs["data"] == {"data": "test"}

def test_request_merges_headers():
    with patch("cuhkit.libs.requests.requests.request") as mock_request:
        mock_request.return_value = MockResponse()

        request("GET", "https://example.com", headers = {"X-Custom": "value"})

        args, kwargs = mock_request.call_args
        assert kwargs["headers"]["User-Agent"] == USER_AGENT
        assert kwargs["headers"]["X-Custom"] == "value"

def test_request_returns_response():
    with patch("cuhkit.libs.requests.requests.request") as mock_request:
        expected = MockResponse(200, "ok")
        mock_request.return_value = expected

        result = request("GET", "https://example.com")
        assert result == expected

def test_is_plain_text_response_with_text_plain():
    response = MockResponse(headers = {"content-type": "text/plain; charset=utf-8"})
    assert is_plain_text_response(response) is True

def test_is_plain_text_response_with_json():
    response = MockResponse(headers = {"content-type": "application/json"})
    assert is_plain_text_response(response) is False

def test_is_plain_text_response_with_no_header():
    response = MockResponse()
    assert is_plain_text_response(response) is False

def test_is_plain_text_response_with_html():
    response = MockResponse(headers = {"content-type": "text/html"})
    assert is_plain_text_response(response) is False

def test_request_propagates_http_error():
    with patch("cuhkit.libs.requests.requests.request") as mock_request:
        mock_request.return_value = MockResponse(404)

        response = request("GET", "https://example.com")

        with pytest.raises(requests.exceptions.HTTPError):
            response.raise_for_status()