import pytest
from freezegun import freeze_time
from pytest_httpx import HTTPXMock

from pytoil import __version__
from pytoil.api import API


def test_headers():
    api = API(username="me", token="notatoken")

    assert api.headers == {
        "Authorization": "token notatoken",
        "User-Agent": f"pytoil/{__version__}",
        "Accept": "application/vnd.github.v4+json",
    }


@pytest.mark.asyncio
async def test_get_repo_names(httpx_mock: HTTPXMock, fake_get_repo_names_response):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_get_repo_names_response, status_code=200
    )

    names = await api.get_repo_names()

    assert names == {
        "dingle",
        "dangle",
        "dongle",
        "a_cool_project",
        "another",
        "yetanother",
        "hello",
    }


@pytest.mark.asyncio
async def test_get_fork_names(httpx_mock: HTTPXMock, fake_get_fork_names_response):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_get_fork_names_response, status_code=200
    )

    names = await api.get_fork_names()

    assert names == {
        "afork",
        "aspoon",
        "anotherfork",
    }


@pytest.mark.asyncio
async def test_check_repo_exists_returns_false_if_not_exists(
    httpx_mock: HTTPXMock, fake_repo_exists_false_response
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_repo_exists_false_response, status_code=200
    )

    exists = await api.check_repo_exists("dave")

    assert exists is False


@pytest.mark.asyncio
async def test_check_repo_exists_returns_true_if_exists(
    httpx_mock: HTTPXMock, fake_repo_exists_true_response
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_repo_exists_true_response, status_code=200
    )

    exists = await api.check_repo_exists("pytoil")

    assert exists is True


@freeze_time("2022-01-16")
@pytest.mark.asyncio
async def test_get_repo_info_good_response(
    httpx_mock: HTTPXMock, fake_repo_info_response
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(url=api.url, json=fake_repo_info_response, status_code=200)

    info = await api.get_repo_info(name="pytoil")

    assert info == {
        "Name": "pytoil",
        "Description": "CLI to automate the development workflow :robot:",
        "Created": "11 months ago",
        "Updated": "19 days ago",
        "Size": "3.2 MB",
        "License": "Apache License 2.0",
        "Remote": True,
    }


@freeze_time("2022-01-16")
@pytest.mark.asyncio
async def test_get_repo_info_no_license(
    httpx_mock: HTTPXMock, fake_repo_info_response_no_license
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_repo_info_response_no_license, status_code=200
    )

    info = await api.get_repo_info(name="pytoil")

    assert info == {
        "Name": "pytoil",
        "Description": "CLI to automate the development workflow :robot:",
        "Created": "11 months ago",
        "Updated": "19 days ago",
        "Size": "3.2 MB",
        "License": None,
        "Remote": True,
    }


@pytest.mark.asyncio
async def test_create_fork(httpx_mock: HTTPXMock):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url="https://api.github.com/repos/someoneelse/project/forks", status_code=201
    )

    await api.create_fork(owner="someoneelse", repo="project")
