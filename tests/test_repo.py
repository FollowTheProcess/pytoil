from __future__ import annotations

from pathlib import Path

import pytest
from freezegun import freeze_time
from pytest_httpx import HTTPXMock
from pytest_mock import MockerFixture

from pytoil.api import API
from pytoil.config import Config
from pytoil.environments import Conda, Flit, Poetry, Requirements, Venv
from pytoil.repo import Repo

PROJECT_ROOT = Path(__file__).parent.parent.resolve()


def test_clone_url():
    repo = Repo(owner="me", name="project", local_path=Path("doesn't/matter"))

    assert repo.clone_url == "https://github.com/me/project.git"


def test_html_url():
    repo = Repo(owner="me", name="project", local_path=Path("doesn't/matter"))

    assert repo.html_url == "https://github.com/me/project"


def test_issues_url():
    repo = Repo(owner="me", name="project", local_path=Path("doesn't/matter"))

    assert repo.issues_url == "https://github.com/me/project/issues"


def test_pulls_url():
    repo = Repo(owner="me", name="project", local_path=Path("doesn't/matter"))

    assert repo.pulls_url == "https://github.com/me/project/pulls"


def test_repo_repr():
    repo = Repo(owner="me", name="project", local_path=Path("somewhere"))
    assert (
        repr(repo)
        == f"Repo(owner='me', name='project', local_path={Path('somewhere')!r})"
    )


@pytest.mark.parametrize(
    "path, exists",
    [
        (PROJECT_ROOT, True),  # This project should hopefully exist!
        (Path("not/here"), False),
    ],
)
def test_exists_local(path: Path, exists: bool):
    repo = Repo(owner="me", name="test", local_path=path)

    assert repo.exists_local() is exists


def test_exists_remote_returns_false_when_remote_doesnt_exist(
    httpx_mock: HTTPXMock, fake_repo_exists_false_response
):
    api = API(username="me", token="something")

    repo = Repo(owner="me", name="test", local_path=Path("doesn't/matter"))

    httpx_mock.add_response(
        url=api.url, json=fake_repo_exists_false_response, status_code=200
    )

    result = repo.exists_remote(api=api)
    assert result is False


def test_exists_remote_returns_true_when_remote_exists(
    httpx_mock: HTTPXMock, fake_repo_exists_true_response
):
    api = API(username="me", token="something")

    repo = Repo(owner="me", name="test", local_path=Path("doesn't/matter"))

    httpx_mock.add_response(
        url=api.url, json=fake_repo_exists_true_response, status_code=200
    )

    result = repo.exists_remote(api=api)
    assert result is True


@freeze_time("2022-01-22 09:00")
def test_remote_info_returns_correct_details(
    httpx_mock: HTTPXMock, fake_repo_info_response
):
    api = API(username="me", token="something")
    repo = Repo(owner="me", name="test", local_path=Path("somewhere"))

    httpx_mock.add_response(url=api.url, json=fake_repo_info_response, status_code=200)

    result = repo._remote_info(api)
    assert result == {
        "Created": "11 months ago",
        "Description": "CLI to automate the development workflow :robot:",
        "License": "Apache License 2.0",
        "Name": "pytoil",
        "Remote": True,
        "Size": "3.2 MB",
        "Updated": "25 days ago",
        "Language": "Python",
    }


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
    repo_folder_with_random_existing_files: Path,
    file: str,
    exists: bool,
):
    repo = Repo(
        owner="me", name="test", local_path=repo_folder_with_random_existing_files
    )

    assert repo._file_exists(file) is exists


@pytest.mark.parametrize(
    "file, expect",
    [
        ("setup.cfg", True),
        ("setup.py", True),
        ("dingle.cfg", False),
        ("dingle.py", False),
        ("pyproject.toml", False),  # Empty pyproject.toml
        ("environment.yml", False),
    ],
)
def test_is_setuptools(
    repo_folder_with_random_existing_files: Path, file: str, expect: bool
):
    repo = Repo(
        owner="me", name="test", local_path=repo_folder_with_random_existing_files
    )

    # Add in the required file to trigger
    repo_folder_with_random_existing_files.joinpath(file).touch()

    assert repo.is_setuptools() is expect


def test_is_setuptools_pep621(project_with_setuptools_pep621_backend: Path):
    repo = Repo(
        owner="me", name="test", local_path=project_with_setuptools_pep621_backend
    )

    assert repo.is_setuptools() is True


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
def test_is_conda(
    repo_folder_with_random_existing_files: Path, file: str, expect: bool
):
    repo = Repo(
        owner="me", name="test", local_path=repo_folder_with_random_existing_files
    )
    # Add in the required file to trigger
    repo_folder_with_random_existing_files.joinpath(file).touch()

    assert repo.is_conda() is expect


def test_is_poetry_true_on_valid_poetry_project(fake_poetry_project: Path):
    repo = Repo(owner="blah", name="test", local_path=fake_poetry_project)

    assert repo.is_poetry() is True


def test_is_poetry_false_on_non_poetry_project(fake_flit_project: Path):
    repo = Repo(owner="blah", name="test", local_path=fake_flit_project)

    assert repo.is_poetry() is False


def test_is_poetry_false_if_no_pyproject_toml():
    repo = Repo(owner="blah", name="test", local_path=Path("nowhere"))

    assert repo.is_poetry() is False


def test_is_poetry_false_if_no_build_system(project_with_no_build_system: Path):
    repo = Repo(owner="blah", name="test", local_path=project_with_no_build_system)

    assert repo.is_poetry() is False


def test_is_poetry_false_if_no_build_backend(project_with_no_build_backend: Path):
    repo = Repo(owner="blah", name="test", local_path=project_with_no_build_backend)

    assert repo.is_poetry() is False


def test_is_flit_true_on_valid_flit_project(fake_flit_project: Path):
    repo = Repo(owner="blah", name="test", local_path=fake_flit_project)

    assert repo.is_flit() is True


def test_is_flit_false_on_non_flit_project(fake_poetry_project: Path):
    repo = Repo(owner="blah", name="test", local_path=fake_poetry_project)

    assert repo.is_flit() is False


def test_is_flit_false_if_no_pyproject_toml():
    repo = Repo(owner="blah", name="test", local_path=Path("nowhere"))

    assert repo.is_flit() is False


def test_is_flit_false_if_no_build_system(project_with_no_build_system: Path):
    repo = Repo(owner="blah", name="test", local_path=project_with_no_build_system)

    assert repo.is_flit() is False


def test_is_flit_false_if_no_build_backend(project_with_no_build_backend: Path):
    repo = Repo(owner="blah", name="test", local_path=project_with_no_build_backend)

    assert repo.is_flit() is False


def test_dispatch_env_correctly_identifies_conda(mocker: MockerFixture):
    mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=True)

    repo = Repo(name="test", owner="me", local_path=Path("somewhere"))

    env = repo.dispatch_env(config=Config())

    assert isinstance(env, Conda)


def test_dispatch_env_correctly_identifies_requirements_txt(
    requirements_project: Path,
):
    repo = Repo(name="test", owner="me", local_path=requirements_project)

    env = repo.dispatch_env(config=Config())

    assert isinstance(env, Requirements)


def test_dispatch_env_correctly_identifies_requirements_dev_txt(
    requirements_dev_project: Path,
):
    repo = Repo(name="test", owner="me", local_path=requirements_dev_project)

    env = repo.dispatch_env(config=Config())

    assert isinstance(env, Requirements)


def test_dispatch_env_correctly_identifies_setuptools(mocker: MockerFixture):
    mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=False)

    mocker.patch("pytoil.repo.Repo.is_setuptools", autospec=True, return_value=True)

    repo = Repo(name="test", owner="me", local_path=Path("somewhere"))

    env = repo.dispatch_env(config=Config())

    assert isinstance(env, Venv)


def test_dispatch_env_correctly_identifies_poetry(fake_poetry_project: Path):
    repo = Repo(name="test", owner="me", local_path=fake_poetry_project)

    env = repo.dispatch_env(config=Config())

    assert isinstance(env, Poetry)


def test_dispatch_env_correctly_identifies_flit(fake_flit_project: Path):
    repo = Repo(name="test", owner="me", local_path=fake_flit_project)

    env = repo.dispatch_env(config=Config())

    assert isinstance(env, Flit)


def test_dispatch_env_returns_none_if_it_cant_detect(mocker: MockerFixture):
    mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=False)

    mocker.patch("pytoil.repo.Repo.is_setuptools", autospec=True, return_value=False)

    repo = Repo(name="test", owner="me", local_path=Path("somewhere"))

    env = repo.dispatch_env(config=Config())

    assert env is None
