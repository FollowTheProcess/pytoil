"""
Tests for the API module.

Author: Tom Fleet
Created: 05/02/2021
"""


import httpx
import pytest
from pytest_httpx import HTTPXMock
from pytest_mock import MockerFixture

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


def test_api_init_default(mocker: MockerFixture, temp_config_file):

    # Patch out the default CONFIG_PATH for our temp file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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


def test_api_repr_default(mocker: MockerFixture, temp_config_file):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        api = API()

        assert api.__repr__() == "API(token='tempfiletoken', username='tempfileuser')"


@pytest.mark.parametrize("bad_status_code", [400, 401, 403, 404, 500, 504, 505])
def test_get_raises_on_bad_status(
    httpx_mock: HTTPXMock, bad_status_code, mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        httpx_mock.add_response(
            url="https://api.github.com/user/repos", status_code=bad_status_code
        )

        api = API(token="definitelynotatoken", username="me")

        with pytest.raises(httpx.HTTPStatusError):
            api.get("user/repos")


def test_get_returns_correct_response(
    httpx_mock: HTTPXMock, fake_api_response, mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        httpx_mock.add_response(
            url="https://api.github.com/user/repos",
            json=fake_api_response,
            status_code=200,
        )

        api = API(token="definitelynotatoken", username="me")

        r = api.get("user/repos")

        assert r == fake_api_response


def test_get_user_repo_correctly_calls_get(mocker: MockerFixture, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo(repo="fakey") == fake_api_response


def test_get_user_repos_correctly_calls_get(mocker: MockerFixture, fake_api_response):

    mocker.patch("pytoil.api.API.get", autospec=True, return_value=fake_api_response)

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repos() == fake_api_response


def test_get_repo_names_correctly_calls_get_repos(
    mocker: MockerFixture, fake_api_response
):

    mocker.patch(
        "pytoil.api.API.get_repos", autospec=True, return_value=fake_api_response
    )

    api = API(token="definitelynotatoken", username="me")

    # The names are contained in the fake_api_response fixture in conftest.py
    assert api.get_repo_names() == ["repo1", "repo2", "repo3"]


@pytest.mark.parametrize(
    "repo_name, description, created_at, updated_at, size, license_dict",
    [
        (
            "repo1",
            "my project",
            "2020-02-27",
            "2020-04-02",
            4096,
            {"id": "some_id", "name": "MIT License"},
        ),
        (
            "repo2",
            "someguys project",
            "2021-01-18",
            "2021-01-23",
            1024,
            {"id": "some_id", "name": "Apache 2.0"},
        ),
        (
            "repo3",
            "somegirls project",
            "2020-07-01",
            "2021-02-28",
            2048,
            {"id": "some_id", "name": "GPL v3"},
        ),
    ],
)
def test_get_repo_info_correctly_calls_get_repo(
    mocker: MockerFixture,
    repo_name,
    description,
    created_at,
    updated_at,
    size,
    license_dict,
):

    # Have the get_repo method just return our made up dict
    mocker.patch(
        "pytoil.api.API.get_repo",
        autospec=True,
        return_value={
            "name": repo_name,
            "description": description,
            "created_at": created_at,
            "updated_at": updated_at,
            "size": size,
            "license": license_dict,
        },
    )

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo_info(repo=repo_name) == {
        "name": repo_name,
        "description": description,
        "created_at": created_at,
        "updated_at": updated_at,
        "size": size,
        "license": license_dict["name"],
    }


def test_get_repo_info_correctly_handles_missing_license(mocker: MockerFixture):

    # Have the get_repo method just return a made up dict with None for license
    mocker.patch(
        "pytoil.api.API.get_repo",
        autospec=True,
        return_value={
            "name": "repo",
            "description": "This is only a test",
            "created_at": "2021-01-02",
            "updated_at": "2021-01-03",
            "size": 1024,
            "license": None,
        },
    )

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo_info(repo="repo")["license"] is None
