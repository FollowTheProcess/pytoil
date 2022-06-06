from __future__ import annotations

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


def test_get_repo_names(httpx_mock: HTTPXMock, fake_get_repo_names_response):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_get_repo_names_response, status_code=200
    )

    names = api.get_repo_names()

    assert names == {
        "dingle",
        "dangle",
        "dongle",
        "a_cool_project",
        "another",
        "yetanother",
        "hello",
    }


def test_check_repo_exists_returns_false_if_not_exists(
    httpx_mock: HTTPXMock, fake_repo_exists_false_response
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_repo_exists_false_response, status_code=200
    )

    exists = api.check_repo_exists(owner="me", name="dave")

    assert exists is False


def test_check_repo_exists_returns_true_if_exists(
    httpx_mock: HTTPXMock, fake_repo_exists_true_response
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_repo_exists_true_response, status_code=200
    )

    exists = api.check_repo_exists(owner="me", name="pytoil")

    assert exists is True


@freeze_time("2022-01-16")
def test_get_repo_info_good_response(httpx_mock: HTTPXMock, fake_repo_info_response):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(url=api.url, json=fake_repo_info_response, status_code=200)

    info = api.get_repo_info(name="pytoil")

    assert info == {
        "Name": "pytoil",
        "Description": "CLI to automate the development workflow :robot:",
        "Created": "11 months ago",
        "Updated": "19 days ago",
        "Size": "3.2 MB",
        "License": "Apache License 2.0",
        "Remote": True,
        "Language": "Python",
    }


@freeze_time("2022-01-16")
def test_get_repo_info_no_license(
    httpx_mock: HTTPXMock, fake_repo_info_response_no_license
):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url=api.url, json=fake_repo_info_response_no_license, status_code=200
    )

    info = api.get_repo_info(name="pytoil")

    assert info == {
        "Name": "pytoil",
        "Description": "CLI to automate the development workflow :robot:",
        "Created": "11 months ago",
        "Updated": "19 days ago",
        "Size": "3.2 MB",
        "License": None,
        "Remote": True,
        "Language": "Python",
    }


def test_create_fork(httpx_mock: HTTPXMock):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(
        url="https://api.github.com/repos/someoneelse/project/forks", status_code=201
    )

    api.create_fork(owner="someoneelse", repo="project")


def test_get_repos(httpx_mock: HTTPXMock, fake_get_repos_response):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(url=api.url, json=fake_get_repos_response, status_code=200)

    data = api.get_repos()

    assert data == [
        {
            "name": "advent_of_code_2020",
            "description": "Retroactively doing AOC2020 in Go.",
            "createdAt": "2022-01-05T16:54:03Z",
            "pushedAt": "2022-01-09T06:55:32Z",
            "diskUsage": 45,
        },
        {
            "name": "advent_of_code_2021",
            "description": "My code for AOC 2021",
            "createdAt": "2021-11-30T12:01:22Z",
            "pushedAt": "2021-12-19T15:10:07Z",
            "diskUsage": 151,
        },
        {
            "name": "aircraft_crashes",
            "description": "Analysis of aircraft crash data.",
            "createdAt": "2021-01-02T19:34:15Z",
            "pushedAt": "2021-01-20T10:35:57Z",
            "diskUsage": 2062,
        },
        {
            "name": "cookie_pypackage",
            "description": "My own version of the Cookiecutter pypackage template",
            "createdAt": "2020-07-04T10:05:36Z",
            "pushedAt": "2021-12-03T08:45:49Z",
            "diskUsage": 734,
        },
        {
            "name": "cv",
            "description": "Repo for my CV, built with JSON Resume.",
            "createdAt": "2021-10-30T15:11:49Z",
            "pushedAt": "2022-01-10T19:50:24Z",
            "diskUsage": 145,
        },
        {
            "name": "eu_energy_analysis",
            "description": "Analysis of the EU Open Power System Data.",
            "createdAt": "2020-12-13T10:50:35Z",
            "pushedAt": "2020-12-24T11:12:34Z",
            "diskUsage": 1834,
        },
        {
            "name": "FollowTheProcess",
            "description": 'My "About Me" Repo',
            "createdAt": "2020-07-14T16:06:52Z",
            "pushedAt": "2022-01-10T20:05:47Z",
            "diskUsage": 14640,
        },
        {
            "name": "followtheprocess.github.io",
            "description": "Repo for my GitHub pages site.",
            "createdAt": "2021-02-19T20:16:05Z",
            "pushedAt": "2021-11-18T19:04:06Z",
            "diskUsage": 10753,
        },
    ]


def test_get_forks(httpx_mock: HTTPXMock, fake_get_forks_response):
    api = API(username="me", token="definitelynotatoken")

    httpx_mock.add_response(url=api.url, json=fake_get_forks_response, status_code=200)

    data = api.get_forks()

    assert data == [
        {
            "name": "nox",
            "diskUsage": 5125,
            "createdAt": "2021-07-01T11:43:36Z",
            "pushedAt": "2022-01-08T11:00:44Z",
            "parent": {"nameWithOwner": "theacodes/nox"},
        },
        {
            "name": "python-launcher",
            "diskUsage": 824,
            "createdAt": "2021-10-25T18:33:11Z",
            "pushedAt": "2021-11-09T07:47:23Z",
            "parent": {"nameWithOwner": "brettcannon/python-launcher"},
        },
    ]
