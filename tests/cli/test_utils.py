"""
Tests for the utils functions in CLI.

Author: Tom Fleet
Created: 11/03/2021
"""

from typing import List, Set

from pytest_mock import MockerFixture

from pytoil.api import API
from pytoil.cli.utils import (
    env_dispatcher,
    get_local_project_list,
    get_local_project_set,
    get_remote_project_list,
    get_remote_project_set,
)
from pytoil.config import Config
from pytoil.environments import CondaEnv, VirtualEnv
from pytoil.repo import Repo


def test_get_local_project_list(fake_projects_dir):

    expected: List[str] = sorted(
        ["project1", "myproject", "dingleproject", "anotherone"], key=str.casefold
    )

    actual_list: List[str] = get_local_project_list(fake_projects_dir)

    assert actual_list == expected


def test_get_local_project_set(fake_projects_dir):

    expected_set: Set[str] = {"project1", "myproject", "dingleproject", "anotherone"}

    actual_set: Set[str] = get_local_project_set(fake_projects_dir)

    assert actual_set == expected_set


def test_get_remote_project_list(mocker: MockerFixture):

    remote_list: List[str] = [
        "Somerepo",
        "Another",
        "yes_repo",
        "helloREpO",
        "Wh4atRepo",
    ]

    fake_api = API(token="hellotoken", username="me")

    mocker.patch(
        "pytoil.cli.utils.API.get_repo_names", autospec=True, return_value=remote_list
    )

    expected_list: List[str] = sorted(remote_list, key=str.casefold)

    actual_list: List[str] = get_remote_project_list(api=fake_api)

    assert actual_list == expected_list


def test_get_remote_project_set(mocker: MockerFixture):

    remote_list: List[str] = [
        "Somerepo",
        "Another",
        "yes_repo",
        "helloREpO",
        "Wh4atRepo",
        "Somerepo",
        "Wh4atRepo",
    ]

    fake_api = API(token="hellotoken", username="me")

    mocker.patch(
        "pytoil.cli.utils.API.get_repo_names", autospec=True, return_value=remote_list
    )

    expected_set: Set[str] = {
        "Somerepo",
        "Another",
        "yes_repo",
        "helloREpO",
        "Wh4atRepo",
    }

    actual_set: Set[str] = get_remote_project_set(api=fake_api)

    assert actual_set == expected_set


def test_env_dispatcher_returns_condaenv_if_repo_is_conda(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch("pytoil.cli.utils.Repo.is_conda", autospec=True, return_value=True)
    mocker.patch(
        "pytoil.cli.utils.Repo.is_setuptools", autospec=True, return_value=False
    )

    fake_repo = Repo(name="dingle")

    env = env_dispatcher(repo=fake_repo)

    assert isinstance(env, CondaEnv)


def test_env_dispatcher_returns_virtualenv_if_repo_is_setuptools(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch("pytoil.cli.utils.Repo.is_conda", autospec=True, return_value=False)
    mocker.patch(
        "pytoil.cli.utils.Repo.is_setuptools", autospec=True, return_value=True
    )

    fake_repo = Repo(name="dingle")

    env = env_dispatcher(repo=fake_repo)

    assert isinstance(env, VirtualEnv)


def test_env_dispatcher_returns_none_if_neither(
    mocker: MockerFixture, fake_projects_dir
):

    fake_config = Config(
        username="test",
        token="testtoken",
        projects_dir=fake_projects_dir,
        vscode=False,
    )

    mocker.patch(
        "pytoil.cli.project.Config.get",
        autospec=True,
        return_value=fake_config,
    )

    mocker.patch("pytoil.cli.utils.Repo.is_conda", autospec=True, return_value=False)
    mocker.patch(
        "pytoil.cli.utils.Repo.is_setuptools", autospec=True, return_value=False
    )

    fake_repo = Repo(name="dingle")

    env = env_dispatcher(repo=fake_repo)

    assert env is None
