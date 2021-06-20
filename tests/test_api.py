"""
Tests for the API module.

Author: Tom Fleet
Created: 19/06/2021
"""

import httpx
import pytest
from pytest_httpx import HTTPXMock

from pytoil.api import API


def test_api_init():

    api = API(username="me", token="sometoken")

    assert api.username == "me"
    assert api.token == "sometoken"
    assert api.baseurl == "https://api.github.com/"
    assert api.headers == {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {api.token}",
    }


def test_api_repr():

    api = API(username="me", token="sometoken")

    assert repr(api) == "API(username='me', token='sometoken')"


@pytest.mark.parametrize("bad_status_code", [400, 401, 403, 404, 500, 504, 505])
def test_get_raises_on_bad_status(httpx_mock: HTTPXMock, bad_status_code):

    httpx_mock.add_response(
        url="https://api.github.com/user/repos", status_code=bad_status_code
    )

    api = API(token="definitelynotatoken", username="me")

    with pytest.raises(httpx.HTTPStatusError):
        api.get("user/repos")


def test_get_returns_correct_response(httpx_mock: HTTPXMock, fake_repos_response):

    httpx_mock.add_response(
        url="https://api.github.com/user/repos",
        json=fake_repos_response,
        status_code=200,
    )

    api = API(token="definitelynotatoken", username="me")

    r = api.get("user/repos")

    assert r == fake_repos_response


def test_get_repo_returns_correct_response(httpx_mock: HTTPXMock, fake_repo_response):

    httpx_mock.add_response(
        url="https://api.github.com/repos/me/pytoil",
        json=fake_repo_response,
        status_code=200,
    )

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo(repo="pytoil") == fake_repo_response


def test_get_repos_returns_correct_response(httpx_mock: HTTPXMock, fake_repos_response):

    httpx_mock.add_response(
        url="https://api.github.com/user/repos?type=owner",
        json=fake_repos_response,
        status_code=200,
    )

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repos() == fake_repos_response


def test_get_repo_names_returns_correct_names(
    httpx_mock: HTTPXMock, fake_repos_response
):

    httpx_mock.add_response(
        url="https://api.github.com/user/repos?type=owner",
        json=fake_repos_response,
        status_code=200,
    )

    api = API(token="definitelynotatoken", username="me")

    # These are the names in the fake_repos_response fixture
    wanted_names = {"repo1", "repo2", "repo3"}

    assert api.get_repo_names() == wanted_names


def test_get_repo_info_returns_correct_info(httpx_mock: HTTPXMock, fake_repo_response):

    httpx_mock.add_response(
        url="https://api.github.com/repos/me/pytoil",
        json=fake_repo_response,
        status_code=200,
    )

    api = API(token="definitelynotatoken", username="me")

    # What we want out
    # This comes from an actual gh response for pytoil
    want = {
        "name": "pytoil",
        "description": "CLI to automate the development workflow.",
        "created_at": "2021-02-04T15:05:23Z",
        "updated_at": "2021-06-13T12:09:52Z",
        "size": 1922,
        "license": "Apache License 2.0",
    }

    assert api.get_repo_info("pytoil") == want


def test_get_repo_info_correctly_handles_missing_license(httpx_mock: HTTPXMock):

    httpx_mock.add_response(
        url="https://api.github.com/repos/me/repo",
        json={
            "name": "repo",
            "description": "This is only a test",
            "created_at": "2021-01-02",
            "updated_at": "2021-01-03",
            "size": 1024,
            "license": None,
        },
        status_code=200,
    )

    api = API(token="definitelynotatoken", username="me")

    assert api.get_repo_info(repo="repo")["license"] is None
