"""
Tests for the repo module.

Author: Tom Fleet
Created: 19/06/2021
"""

from pathlib import Path
from typing import NamedTuple

import pytest
from pytest_httpx import HTTPXMock
from pytest_mock import MockerFixture

from pytoil.api import API
from pytoil.environments import Conda, Venv
from pytoil.exceptions import RepoNotFoundError
from pytoil.repo import Repo

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def test_repo_init():

    repo = Repo(owner="me", name="test", local_path=Path("some/dir/test"))

    assert repo.owner == "me"
    assert repo.name == "test"
    assert repo.local_path == Path("some/dir/test")
    assert repo.clone_url == "https://github.com/me/test.git"
    assert repo.html_url == "https://github.com/me/test"


def test_repo_repr():

    repo = Repo(owner="me", name="test", local_path=Path("some/dir/test"))

    assert (
        repr(repo)
        == f"Repo(owner='me', name='test', local_path={repr(Path('some/dir/test'))})"
    )


def test_exists_local_returns_true_when_path_exists():

    # Make a fake repo but give it this projects path so we know
    # it should exist

    repo = Repo(owner="me", name="test", local_path=PROJECT_ROOT)

    assert repo.exists_local() is True


def test_exists_local_returns_false_when_path_doesnt_exist():

    repo = Repo(owner="me", name="test", local_path=Path("not/here"))

    assert repo.exists_local() is False


def test_exists_remote_returns_true_when_remote_exists(
    httpx_mock: HTTPXMock, fake_repo_response
):

    api = API(username="me", token="something")

    repo = Repo(owner="me", name="test", local_path=Path("doesnt/matter"))

    # The way we test for a repo existing is look for a bad status code
    # 4xx or 5xx

    # Let's make httpx return a good code to indicate this repo exists
    httpx_mock.add_response(
        url="https://api.github.com/repos/me/test",
        status_code=200,
        json=fake_repo_response,
    )

    assert repo.exists_remote(api=api) is True


def test_exists_remote_returns_false_when_remote_doesnt_exist(httpx_mock: HTTPXMock):

    api = API(username="me", token="something")

    repo = Repo(owner="me", name="test", local_path=Path("doesnt/matter"))

    # The way we test for a repo existing is look for a bad status code
    # 4xx or 5xx

    # Let's make httpx return a bad code to simulate this repo not existing
    httpx_mock.add_response(url="https://api.github.com/repos/me/test", status_code=404)

    assert repo.exists_remote(api=api) is False


@pytest.mark.parametrize(
    "repo_name, description, created_at, updated_at, size, license_name, exist_local,"
    + " exist_remote",
    [
        (
            "repo1",
            "my project",
            "2020-02-27",
            "2020-04-02",
            4096,
            "MIT License",
            True,
            True,
        ),
        (
            "repo2",
            "someguys project",
            "2021-01-18",
            "2021-01-23",
            1024,
            "Apache 2.0",
            False,
            True,
        ),
        (
            "repo3",
            "somegirls project",
            "2020-07-01",
            "2021-02-28",
            2048,
            "GPL v3",
            True,
            True,
        ),
    ],
)
def test_info_on_remote_repo(
    mocker: MockerFixture,
    repo_name,
    description,
    created_at,
    updated_at,
    size,
    license_name,
    exist_remote,
    exist_local,
):
    """
    If a repo exists remotely, regardless of whether or not it is also
    local. info should return info from the API as it is more detailed.
    """

    # Convince it the repo exists remotely and locally
    mocker.patch(
        "pytoil.repo.Repo.exists_remote", autospec=True, return_value=exist_remote
    )
    mocker.patch(
        "pytoil.repo.Repo.exists_local", autospec=True, return_value=exist_local
    )

    api = API(username="me", token="sometoken")

    # Have the get_repo_info method just return our made up dict
    mocker.patch(
        "pytoil.api.API.get_repo_info",
        autospec=True,
        return_value={
            "name": repo_name,
            "description": description,
            "created_at": created_at,
            "updated_at": updated_at,
            "size": size,
            "license": license_name,
            "local": exist_local,
            "remote": exist_remote,
        },
    )

    repo = Repo(name=repo_name, owner="me", local_path=Path("somewhere"))

    assert repo.info(api=api) == {
        "name": repo_name,
        "description": description,
        "created_at": created_at,
        "updated_at": updated_at,
        "size": size,
        "license": license_name,
        "local": exist_local,
        "remote": exist_remote,
    }


@pytest.mark.parametrize(
    "repo_name, created_at, updated_at, size, exist_local, exist_remote",
    [
        (
            "repo1",
            "2021-03-01 10:43:19",
            "2021-03-01 10:48:19",
            4096,
            True,
            False,
        ),
        (
            "repo2",
            "2021-03-01 10:43:19",
            "2021-03-01 10:48:19",
            1024,
            True,
            False,
        ),
        (
            "repo3",
            "2021-03-01 10:43:19",
            "2021-03-01 10:48:19",
            2048,
            True,
            False,
        ),
    ],
)
def test_info_on_local_only_repo(
    mocker: MockerFixture,
    repo_name,
    created_at,
    updated_at,
    size,
    exist_remote,
    exist_local,
):
    """
    If a repo exists locally only, we should instead get some info from Path.stat.
    This one is quite complicated because you can't mock out datetime
    so instead we:

    - patch out everything related to whether or not the repo exists
    - Create a fake dataclass `FakeStat`
    - This FakeStat houses the unix timestamps that datetime.strftime can operate on
    - In the parametrize we have the strftime outputs for those timestamps
    """

    # Convince it the repo exists remotely and locally
    mocker.patch(
        "pytoil.repo.Repo.exists_remote", autospec=True, return_value=exist_remote
    )
    mocker.patch(
        "pytoil.repo.Repo.exists_local", autospec=True, return_value=exist_local
    )

    # Have the get_repo_info method just return our made up dict
    mocker.patch(
        "pytoil.api.API.get_repo_info",
        autospec=True,
        return_value={
            "name": repo_name,
            "created_at": created_at,
            "updated_at": updated_at,
            "size": size,
            "local": exist_local,
            "remote": exist_remote,
        },
    )

    class FakeStat(NamedTuple):
        st_ctime = 1614595399
        st_mtime = 1614595699
        st_size = size

    mocker.patch("pytoil.repo.repo.Path.stat", autospec=True, return_value=FakeStat())

    api = API(username="me", token="sometoken")
    repo = Repo(name=repo_name, owner="me", local_path=Path(repo_name))

    assert repo.info(api=api) == {
        "name": repo_name,
        "created_at": created_at,
        "updated_at": updated_at,
        "size": size,
        "local": exist_local,
        "remote": exist_remote,
    }


def test_repo_info_raises_if_doesnt_exist_locally_or_remotely(mocker: MockerFixture):

    # Convince it the repo does not exist remotely or locally
    mocker.patch("pytoil.repo.Repo.exists_remote", autospec=True, return_value=False)
    mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

    api = API(username="me", token="sometoken")

    with pytest.raises(RepoNotFoundError):
        repo = Repo(name="blah", owner="me", local_path=Path("who/cares"))
        repo.info(api=api)


@pytest.mark.parametrize(
    "file, exists",
    [
        ("here.txt", True),
        ("i_exist.yml", True),
        ("hello.py", True),
        ("me_too.json", True),
        ("not_me_though.csv", False),
        ("me_neither.toml", False),
        ("i_never_existed.cfg", False),
        ("what_file.ini", False),
    ],
)
def test_does_file_exist(
    repo_folder_with_random_existing_files,
    file,
    exists,
):

    folder: Path = repo_folder_with_random_existing_files
    repo = Repo(owner="me", name="test", local_path=folder)

    # Test the file exists method
    assert repo.file_exists(file) is exists


@pytest.mark.parametrize(
    "file, expect",
    [
        ("setup.cfg", True),
        ("setup.py", True),
        ("dingle.cfg", False),
        ("dingle.py", False),
        ("pyproject.toml", False),
        ("environment.yml", False),
    ],
)
def test_is_setuptools(repo_folder_with_random_existing_files, file, expect):

    folder: Path = repo_folder_with_random_existing_files
    repo = Repo(owner="me", name="test", local_path=folder)

    # Add in the required file to trigger
    folder.joinpath(file).touch()

    assert repo.is_setuptools() is expect


@pytest.mark.parametrize(
    "file, expect",
    [
        ("setup.cfg", False),
        ("setup.py", False),
        ("dingle.cfg", False),
        ("dingle.py", False),
        ("pyproject.toml", False),
        ("environment.yml", True),
    ],
)
def test_is_conda(repo_folder_with_random_existing_files, file, expect):

    folder: Path = repo_folder_with_random_existing_files
    repo = Repo(owner="me", name="test", local_path=folder)

    # Add in the required file to trigger
    folder.joinpath(file).touch()

    assert repo.is_conda() is expect


@pytest.mark.parametrize(
    "file, expect",
    [
        ("setup.cfg", False),
        ("setup.py", True),
        ("dingle.cfg", False),
        ("dingle.py", False),
        ("pyproject.toml", False),
        ("environment.yml", False),
    ],
)
def test_is_editable(repo_folder_with_random_existing_files, file, expect):

    folder: Path = repo_folder_with_random_existing_files
    repo = Repo(owner="me", name="test", local_path=folder)

    # Add in the required file to trigger
    folder.joinpath(file).touch()

    assert repo.is_editable() is expect


@pytest.mark.parametrize(
    "file, expect",
    [
        ("setup.cfg", False),
        ("setup.py", False),
        ("dingle.cfg", False),
        ("dingle.py", False),
        ("pyproject.toml", False),
        ("environment.yml", False),
    ],
)
def test_is_PEP517(repo_folder_with_random_existing_files, file, expect):

    folder: Path = repo_folder_with_random_existing_files
    repo = Repo(owner="me", name="test", local_path=folder)

    # Add in the required file to trigger
    folder.joinpath(file).touch()

    # We haven't written a build system to the toml so should
    # return False
    assert repo.is_PEP517() is expect


def test_is_PEP517_detects_build_system():

    # This project has a valid pyproject.toml
    # let's use that!
    this_project = Path(__file__).parent.parent.resolve()
    repo = Repo(owner="FollowTheProcess", name="pytoil", local_path=this_project)

    assert repo.is_PEP517() is True


def test_dispatch_env_correctly_identifies_conda(mocker: MockerFixture):

    mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=True)

    repo = Repo(name="test", owner="me", local_path=Path("somewhere"))

    env = repo.dispatch_env()

    assert isinstance(env, Conda)


def test_dispatch_env_correctly_identifies_venv(mocker: MockerFixture):

    mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=False)

    mocker.patch("pytoil.repo.Repo.is_setuptools", autospec=True, return_value=True)

    repo = Repo(name="test", owner="me", local_path=Path("somewhere"))

    env = repo.dispatch_env()

    assert isinstance(env, Venv)


def test_dispatch_env_returns_none_if_it_cant_detect(mocker: MockerFixture):

    mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=False)

    mocker.patch("pytoil.repo.Repo.is_setuptools", autospec=True, return_value=False)

    repo = Repo(name="test", owner="me", local_path=Path("somewhere"))

    env = repo.dispatch_env()

    assert env is None
