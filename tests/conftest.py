"""
Test fixtures and other handy stuff.

Author: Tom Fleet
Created: 18/06/2021
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Union

import pytest
import toml
import yaml

TESTDATA = Path(__file__).parent.joinpath("testdata")
REPO_JSON = TESTDATA / "repo.json"


@pytest.fixture
def temp_config_file(tmp_path_factory):
    """
    Returns a totally valid config file.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, str] = {
        "username": "tempfileuser",
        "token": "tempfiletoken",
        "projects_dir": "/Users/tempfileuser/projects",
        "vscode": True,
        "common_packages": ["black", "flake8", "mypy"],
        "init_on_new": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def fake_repos_response():
    """
    Made up response with a list of repos.

    I tried using an actual snipped from my own user/repos JSON
    but it was too big to deal with efficiently during tests.

    Plus when dealing with a list of repo's pytoil only really
    cares about the name
    """

    response: Dict[str, Any] = [
        {"name": "repo1", "owner": "me", "blah": "bleh"},
        {"name": "repo2", "owner": "someguy", "blah": "bluh"},
        {"name": "repo3", "owner": "somegirl", "blah": "blah"},
    ]

    return response


@pytest.fixture
def fake_repo_response():
    """
    Actual repo JSON taken from this repo.

    Pytoil gets much more out of an individual repo's JSON
    response so this is an actual response.
    """

    with open(REPO_JSON, mode="r", encoding="utf-8") as f:
        response_dict = json.load(f)

    return response_dict


@pytest.fixture
def fake_projects_dir(tmp_path_factory):
    """
    Returns a fake projects directory complete
    with subdirectories mocking development projects.
    """

    project_names: List[str] = [
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
def temp_environment_yml(tmp_path_factory):
    """
    Returns a valid temporary environment.yml file
    """

    env_file: Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

    fake_env_info: Dict[str, Union[str, List[str]]] = {
        "name": "my_yml_env",
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

    with open(env_file, mode="w", encoding="utf-8") as f:
        yaml.dump(fake_env_info, f)

    return env_file


@pytest.fixture
def bad_temp_environment_yml(tmp_path_factory):
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

    with open(env_file, "w") as f:
        yaml.dump(fake_env_info, f)

    return env_file


@pytest.fixture
def bad_temp_environment_yml_2(tmp_path_factory):
    """
    Returns an invalid temporary environment.yml file
    """

    env_file: Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

    # name must be a string
    fake_env_info = {
        "name": ["list", "of", "names"],
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

    with open(env_file, "w") as f:
        yaml.dump(fake_env_info, f)

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

    files: List[str] = ["here.txt", "i_exist.yml", "hello.py", "me_too.json"]

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
        toml.dump(build_system, f)

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
        toml.dump(build_system, f)

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
        toml.dump(build_system, f)

    return folder
