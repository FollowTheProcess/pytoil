"""
Tests for the API module.

Author: Tom Fleet
Created: 05/02/2021
"""


import httpx
import pytest
from pytest_httpx import HTTPXMock

import pytoil
from pytoil.api import API
from pytoil.exceptions import APIRequestError


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
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

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

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

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


@pytest.mark.parametrize("bad_status_code", [400, 401, 403, 404, 500, 504, 505])
def test_get_raises_on_bad_status(
    httpx_mock: HTTPXMock, bad_status_code, mocker, temp_config_file
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        httpx_mock.add_response(
            url="https://api.github.com/user/repos", status_code=bad_status_code
        )

        api = API(token="definitelynotatoken", username="me")

        with pytest.raises(httpx.HTTPStatusError):
            api.get("user/repos")


def test_get_returns_correct_response(
    httpx_mock: HTTPXMock, fake_api_response, mocker, temp_config_file
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        httpx_mock.add_response(
            url="https://api.github.com/user/repos",
            json=fake_api_response,
            status_code=200,
        )

        api = API(token="definitelynotatoken", username="me")

        r = api.get("user/repos")

        assert r == fake_api_response


@pytest.mark.parametrize("bad_status_code", [400, 401, 403, 404, 500, 504, 505])
def test_post_raises_on_bad_status(
    httpx_mock: HTTPXMock, mocker, temp_config_file, bad_status_code
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        httpx_mock.add_response(
            url="https://api.github.com/user/repos", status_code=bad_status_code
        )

        api = API(token="definitelynotatoken", username="me")

        with pytest.raises(httpx.HTTPStatusError):
            api.post("user/repos")


def test_post_returns_correct_response(
    httpx_mock: HTTPXMock, fake_api_response, mocker, temp_config_file
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        httpx_mock.add_response(
            url="https://api.github.com/user/repos",
            json=fake_api_response,
            status_code=200,
        )

        api = API(token="definitelynotatoken", username="me")

        r = api.post("user/repos")

        assert r == fake_api_response


def test_get_user_repo_correctly_calls_get(mocker, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo(repo="fakey") == fake_api_response


def test_get_user_repos_correctly_calls_get(mocker, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repos() == fake_api_response


def test_get_repo_names_correctly_calls_get_repos(mocker, fake_api_response):

    mocker.patch(
        "pytoil.api.API.get_repos", autospec=True, return_value=fake_api_response
    )

    api = API(token="definitelynotatoken", username="me")

    # The names are contained in the fake_api_response fixture in conftest.py
    assert api.get_repo_names() == ["repo1", "repo2", "repo3"]


def test_fork_repo_raises_if_owner_matches_username(mocker, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        api = API(token="notatoken", username="hello")

        with pytest.raises(APIRequestError):
            api.fork_repo(owner="hello", name="project")


def test_fork_repo_returns_if_owner_doesnt_match_username(mocker, temp_config_file):

    # Patch the default config file location to our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out api.post to return some arbitrary json
        # and more importantly, not actually hit the GitHub API
        mocker.patch(
            "pytoil.api.API.post",
            autospec=True,
            return_value={"arbitrary": "json", "blob": "yes"},
        )

        api = API(token="notatoken", username="hello")

        # Fork a repo with a different user name
        response = api.fork_repo(owner="someoneelse", name="project")

        assert response == {"arbitrary": "json", "blob": "yes"}
