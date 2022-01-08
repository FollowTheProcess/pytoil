from pathlib import Path
from typing import Union

import aiofiles
import pytest
import tomlkit
import yaml


@pytest.fixture
def fake_get_repo_names_response():
    """
    Response snippet for the get_repo_names GraphQL
    query.
    """

    return {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [
                        {"name": "dingle"},
                        {"name": "dongle"},
                        {"name": "dangle"},
                        {"name": "a_cool_project"},
                        {"name": "another"},
                        {"name": "yetanother"},
                        {"name": "hello"},
                    ]
                }
            }
        }
    }


@pytest.fixture
def fake_get_fork_names_response():
    """
    Response snippet for the get_fork_names
    graphQL query.
    """
    return {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [
                        {"name": "afork"},
                        {"name": "aspoon"},
                        {"name": "anotherfork"},
                    ]
                }
            }
        }
    }


@pytest.fixture
def fake_repo_exists_false_response():
    """
    Response snippet for the check_repo_exists GraphQL
    query when the requested repo does not exist.
    """
    return {
        "data": {"repository": None},
        "errors": [
            {
                "type": "NOT_FOUND",
                "path": ["repository"],
                "locations": [{"line": 7, "column": 3}],
                "message": (
                    "Could not resolve to a Repository with the name"
                    " 'FollowTheProcess/dave'."
                ),
            }
        ],
    }


@pytest.fixture
def fake_repo_exists_true_response():
    """
    Response snippet for the check_repo_exists GraphQL
    query when the requested repo exists.
    """
    return {"data": {"repository": {"name": "pytoil"}}}


@pytest.fixture
def fake_repo_info_response():
    """
    Response snippet for the get_repo_info GraphQL
    query.
    """
    return {
        "data": {
            "repository": {
                "name": "pytoil",
                "description": "CLI to automate the development workflow :robot:",
                "createdAt": "2021-02-04T15:05:23Z",
                "updatedAt": "2021-12-27T13:31:53Z",
                "diskUsage": 3153,
                "licenseInfo": {"name": "Apache License 2.0"},
            }
        }
    }


@pytest.fixture
def fake_repo_info_response_no_license():
    """
    Response snippet for the get_repo_info GraphQL
    query.
    """
    return {
        "data": {
            "repository": {
                "name": "pytoil",
                "description": "CLI to automate the development workflow :robot:",
                "createdAt": "2021-02-04T15:05:23Z",
                "updatedAt": "2021-12-27T13:31:53Z",
                "diskUsage": 3153,
                "licenseInfo": None,
            }
        }
    }


@pytest.fixture
def fake_projects_dir(tmp_path_factory):
    """
    Returns a fake projects directory complete
    with subdirectories mocking development projects.
    """

    project_names: list[str] = [
        "project1",
        "myproject",
        "dingleproject",
        "anotherone",
        ".ishouldnt_show_up",
    ]

    projects_dir: Path = tmp_path_factory.mktemp("projects")

    for project_name in project_names:
        project_path = projects_dir.joinpath(project_name)
        project_path.mkdir()

    return projects_dir


@pytest.fixture
async def temp_environment_yml(tmp_path_factory):
    """
    Returns a valid temporary environment.yml file
    """

    env_file: Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

    fake_env_info: dict[str, Union[str, list[str]]] = {
        "name": "testy",
        "channels": ["defaults", "conda-forge"],
        "dependencies": [
            "python=3",
            "invoke",
            "black",
            "flake8",
            "isort",
            "mypy",
            "rich",
            "numpy",
            "requests",
            "pandas",
        ],
    }

    async with aiofiles.open(env_file, mode="w", encoding="utf-8") as f:
        content = yaml.dump(fake_env_info)
        await f.write(content)

    return env_file


@pytest.fixture
async def bad_temp_environment_yml(tmp_path_factory):
    """
    Returns an invalid temporary environment.yml file
    """

    env_file: Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

    # name must be a string
    fake_env_info = {
        "name": 300,
        "channels": ["defaults", "conda-forge"],
        "dependencies": [
            "python>3.7",
            "invoke",
            "black",
            "flake8",
            "isort",
            "mypy",
            "rich",
            "requests",
            "numpy",
            "pandas",
        ],
    }

    async with aiofiles.open(env_file, "w") as f:
        content = yaml.dump(fake_env_info)
        await f.write(content)

    return env_file


@pytest.fixture
def fake_home_folder_miniconda(tmp_path_factory):
    """
    Returns a faked $HOME folder. Should be used as the return
    value from pathlib.Path.home().
    Designed to test the auto detection of conda environment
    storage directory.
    """

    fake_home: Path = tmp_path_factory.mktemp("home")

    miniconda = fake_home.joinpath("miniconda3/envs")
    miniconda.mkdir(parents=True)

    return fake_home


@pytest.fixture
def fake_home_folder_anaconda(tmp_path_factory):
    """
    Returns a faked $HOME folder. Should be used as the return
    value from pathlib.Path.home().
    Designed to test the auto detection of conda environment
    storage directory.
    """

    fake_home: Path = tmp_path_factory.mktemp("home")

    anaconda = fake_home.joinpath("anaconda3/envs")
    anaconda.mkdir(parents=True)

    return fake_home


@pytest.fixture
def fake_home_folder_miniforge(tmp_path_factory):
    """
    Returns a faked $HOME folder. Should be used as the return
    value from pathlib.Path.home().
    Designed to test the auto detection of conda environment
    storage directory.
    """

    fake_home: Path = tmp_path_factory.mktemp("home")

    anaconda = fake_home.joinpath("miniforge3/envs")
    anaconda.mkdir(parents=True)

    return fake_home


@pytest.fixture
def fake_home_folder_mambaforge(tmp_path_factory):
    """
    Returns a faked $HOME folder. Should be used as the return
    value from pathlib.Path.home().
    Designed to test the auto detection of conda environment
    storage directory.
    """

    fake_home: Path = tmp_path_factory.mktemp("home")

    anaconda = fake_home.joinpath("mambaforge/envs")
    anaconda.mkdir(parents=True)

    return fake_home


@pytest.fixture
def fake_home_folder_no_conda(tmp_path_factory):
    """
    Returns a faked $HOME but without any conda dirs.
    To test whether get_envs_dir raises correctly.
    """

    fake_home: Path = tmp_path_factory.mktemp("home")

    return fake_home


@pytest.fixture
def repo_folder_with_random_existing_files(tmp_path_factory):
    """
    Returns a temporary directory containing a few random files
    to test methods which check for a files existence within
    a certain directory.
    """

    folder: Path = tmp_path_factory.mktemp("myrepo")

    files: list[str] = ["here.txt", "i_exist.yml", "hello.py", "me_too.json"]

    for file in files:
        # Create each file under the myrepo folder
        folder.joinpath(file).touch()

    return folder


@pytest.fixture
def project_with_no_build_system(tmp_path_factory):
    """
    Returns a temporary directory containing a
    pyproject.toml but this file does not specify
    a build-system, which is bad.
    """

    # Create the folder and pyproject.toml file
    folder: Path = tmp_path_factory.mktemp("myrepo")
    pyproject_toml = folder.joinpath("pyproject.toml")
    pyproject_toml.touch()

    return folder


@pytest.fixture
def project_with_no_build_backend(tmp_path_factory):
    """
    Returns a temporary directory containing a
    pyproject.toml.
    This time we do write a 'build-system' but no
    'build-backend'.
    """

    # Create the folder and pyproject.toml file
    folder: Path = tmp_path_factory.mktemp("myrepo")
    pyproject_toml = folder.joinpath("pyproject.toml")
    pyproject_toml.touch()

    # Create some fake build-system
    build_system = {
        "build-system": {
            "requires": ["poetry-core>=1.0.0"],
        },
    }

    with open(pyproject_toml, mode="w", encoding="utf-8") as f:
        tomlkit.dump(build_system, f)

    return folder


@pytest.fixture
def fake_poetry_project(tmp_path_factory):
    """
    Returns a temporary directory containing a
    valid poetry pyproject.toml file.
    """

    # Create the folder and pyproject.toml file
    folder: Path = tmp_path_factory.mktemp("myrepo")
    pyproject_toml = folder.joinpath("pyproject.toml")
    pyproject_toml.touch()

    # Create some fake poetry content
    build_system = {
        "build-system": {
            "requires": ["poetry-core>=1.0.0"],
            "build-backend": "poetry.core.masonry.api",
        },
    }

    with open(pyproject_toml, mode="w", encoding="utf-8") as f:
        tomlkit.dump(build_system, f)

    return folder


@pytest.fixture
def fake_flit_project(tmp_path_factory):
    """
    Returns a temporary directory containing a
    valid flit pyproject.toml file.
    """

    # Create the folder and pyproject.toml file
    folder: Path = tmp_path_factory.mktemp("myrepo")
    pyproject_toml = folder.joinpath("pyproject.toml")
    pyproject_toml.touch()

    # Create some fake poetry content
    build_system = {
        "build-system": {
            "requires": ["flit_core >=2,<4"],
            "build-backend": "flit_core.buildapi",
        },
    }

    with open(pyproject_toml, mode="w", encoding="utf-8") as f:
        tomlkit.dump(build_system, f)

    return folder


@pytest.fixture
def requirements_dev_project(tmp_path_factory):
    """
    Returns a temp directory containing a requirements_dev.txt
    file.
    """

    folder: Path = tmp_path_factory.mktemp("myrepo")
    req_dev_txt = folder.joinpath("requirements_dev.txt")
    req_dev_txt.touch()

    return folder


@pytest.fixture
def requirements_project(tmp_path_factory):
    """
    Returns a temp directory containing a requirements.txt
    file.
    """

    folder: Path = tmp_path_factory.mktemp("myrepo")
    req_txt = folder.joinpath("requirements.txt")
    req_txt.touch()

    return folder
