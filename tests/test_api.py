"""
Tests for the API module.

Author: Tom Fleet
Created: 05/02/2021
"""

import urllib.error

import pytest

import pytoil
from pytoil.api import API


def test_api_init_passed():

    api = API(token="definitelynotatoken", username="me")

    assert api.token == "definitelynotatoken"
    assert api.username == "me"
    assert api.baseurl == "https://api.github.com/"
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token definitelynotatoken",
    }


def test_api_init_default(mocker, temp_config_file):

    # Patch out the default CONFIG_PATH for our temp file
    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # Also patch out the return from pathlib.Path.exists to trick
        # it into thinking the projects_dir exists
        mocker.patch(
            "pytoil.config.pathlib.Path.exists", autospec=True, return_value=True
        )

        api = API()

        assert api.token == "tempfiletoken"
        assert api.username == "tempfileuser"
        assert api.baseurl == "https://api.github.com/"
        assert api.headers == {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "token tempfiletoken",
        }


def test_api_repr_passed():

    api = API(token="definitelynotatoken", username="me")

    assert api.__repr__() == "API(token='definitelynotatoken', username='me')"


def test_api_repr_default(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # Also patch out the return from pathlib.Path.exists to trick
        # it into thinking the projects_dir exists
        mocker.patch(
            "pytoil.config.pathlib.Path.exists", autospec=True, return_value=True
        )

        api = API()

        assert api.__repr__() == "API(token='tempfiletoken', username='tempfileuser')"


def test_api_setters():

    api = API(token="definitelynotatoken", username="me")

    # Assert properties before
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "token definitelynotatoken",
    }
    assert api.token == "definitelynotatoken"
    assert api.username == "me"

    # Change properties
    api.headers = {"dingle": "dongle", "dangle": "dungle"}
    api.token = "anotherfaketoken"
    api.username = "someoneelse"

    # Assert after
    assert api.headers == {"dingle": "dongle", "dangle": "dungle"}
    assert api.token == "anotherfaketoken"
    assert api.username == "someoneelse"


def test_get_raises_on_invalid_request(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # Also patch out the return from pathlib.Path.exists to trick
        # it into thinking the projects_dir exists
        mocker.patch(
            "pytoil.config.pathlib.Path.exists", autospec=True, return_value=True
        )

        api = API()

        mocker.patch(
            "pytoil.api.urllib.request.urlopen",
            autospec=True,
            side_effect=urllib.error.HTTPError(
                "https://api.github.com/not/here",
                404,
                "Not Found",
                api.headers,
                None,
            ),
        )

        with pytest.raises(urllib.error.HTTPError):
            api.get("not/here")


def test_get_user_repo_correctly_calls_get(mocker, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo(repo="fakey") == fake_api_response


def test_get_user_repos_correctly_calls_get(mocker, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repos() == fake_api_response
