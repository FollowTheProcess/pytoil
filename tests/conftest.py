"""
pytest fixtures and other good stuff

Author: Tom Fleet
Created: 05/02/2021
"""

import json
import pathlib
from typing import Any, Dict, List, Union

import pytest
import yaml


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
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_missing_key(tmp_path_factory):
    """
    Returns an otherwise-valid config file with a missing key.
    In this case, the `token` key.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, str] = {
        "username": "tempfileuser",
        "projects_dir": "/Users/tempfileuser/projects",
        "vscode": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_key_with_blank_value(tmp_path_factory):
    """
    Returns an otherwise-valid config file but one of the keys
    has a blank value.

    In this case, the `token` key.

    A blank value is interpreted by pyyaml as None.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, Union[str, None]] = {
        "username": "tempfileuser",
        "token": None,
        "projects_dir": "/Users/tempfileuser/projects",
        "vscode": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_misspelled_key(tmp_path_factory):
    """
    Returns an otherwise-valid config file with a misspelled key.
    In this case, the `token` key.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, str] = {
        "username": "tempfileuser",
        "terrrken": "tempfiletoken",
        "projects_dir": "/Users/tempfileuser/projects",
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_missing_username(tmp_path_factory):
    """
    Returns an otherwise-valid config file but the username key
    is blank

    A blank value is interpreted by pyyaml as None.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, Union[str, None]] = {
        "username": None,
        "token": "tempfiletoken",
        "projects_dir": "/Users/tempfileuser/projects",
        "vscode": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_missing_token(tmp_path_factory):
    """
    Returns an otherwise-valid config file but the token key
    is blank

    A blank value is interpreted by pyyaml as None.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, Union[str, None]] = {
        "username": "tempfileuser",
        "token": None,
        "projects_dir": "/Users/tempfileuser/projects",
        "vscode": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_missing_projects_dir(tmp_path_factory):
    """
    Returns an otherwise-valid config file but the projects_dir key
    is blank

    A blank value is interpreted by pyyaml as None.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, Union[str, None]] = {
        "username": "tempfileuser",
        "token": "tempfiletoken",
        "projects_dir": None,
        "vscode": True,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def temp_config_file_missing_vs_code(tmp_path_factory):
    """
    Returns an otherwise-valid config file but the projects_dir key
    is blank

    A blank value is interpreted by pyyaml as None.
    """

    config_file = tmp_path_factory.mktemp("temp").joinpath(".pytoil.yml")

    yaml_dict: Dict[str, Union[str, None]] = {
        "username": "tempfileuser",
        "token": "tempfiletoken",
        "projects_dir": "/Users/tempfileuser/projects",
        "vscode": None,
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def fake_api_response():

    response: Dict[str, Any] = [
        {"name": "repo1", "owner": "me", "blah": "bleh"},
        {"name": "repo2", "owner": "someguy", "blah": "bluh"},
        {"name": "repo3", "owner": "somegirl", "blah": "blah"},
    ]

    return response


@pytest.fixture
def temp_environment_yml(tmp_path_factory):
    """
    Returns a valid temporary environment.yml file
    """

    env_file: pathlib.Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

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

    with open(env_file, "w") as f:
        yaml.dump(fake_env_info, f)

    return env_file


@pytest.fixture
def bad_temp_environment_yml(tmp_path_factory):
    """
    Returns an invalid temporary environment.yml file
    """

    env_file: pathlib.Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

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

    env_file: pathlib.Path = tmp_path_factory.mktemp("temp").joinpath("environment.yml")

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
def repo_folder_with_random_existing_files(tmp_path_factory):
    """
    Returns a temporary directory containing a few random files
    to test methods which check for a files existence within
    a certain directory.
    """

    folder: pathlib.Path = tmp_path_factory.mktemp("myrepo")

    files: List[str] = ["here.txt", "i_exist.yml", "hello.py", "me_too.json"]

    for file in files:
        # Create each file under the myrepo folder
        folder.joinpath(file).touch()

    return folder


@pytest.fixture
def fake_vscode_workspace_settings(tmp_path_factory):
    """
    Returns a temporary JSON file with fake
    vscode workspace settings inside.
    """

    fake_project_root: pathlib.Path = tmp_path_factory.mktemp("fakeproject")
    vscode_folder = fake_project_root.joinpath(".vscode")
    vscode_folder.mkdir(parents=True)

    settings_json = vscode_folder.joinpath("settings.json")
    settings_json.touch()

    settings_dict: Dict[str, Any] = {
        "editor.suggestSelection": True,
        "code-runner.runInTerminal": False,
        "python.linting.mypyEnabled": True,
        "python.linting.blackPath": "usr/bin/black",
        "randomSetting": "yes",
        "HowHardThisIsToComeUpWith": 10,
        "python.pythonPath": "/usr/bin/python",
        "python.testing.pytestEnabled": False,
    }

    with open(settings_json, mode="w", encoding="utf-8") as f:
        json.dump(settings_dict, f, sort_keys=True, indent=4)

    return settings_json


@pytest.fixture
def fake_home_folder_miniconda(tmp_path_factory):
    """
    Returns a faked $HOME folder. Should be used as the return
    value from pathlib.Path.home().

    Designed to test the auto detection of conda environment
    storage directory.
    """

    fake_home: pathlib.Path = tmp_path_factory.mktemp("home")

    # Add in the miniconda3/envs folder
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

    fake_home: pathlib.Path = tmp_path_factory.mktemp("home")

    # Add in the anaconda3/envs folder
    anaconda = fake_home.joinpath("anaconda3/envs")
    anaconda.mkdir(parents=True)

    return fake_home


@pytest.fixture
def fake_home_folder_neither(tmp_path_factory):
    """
    Returns a faked $HOME but without any conda dirs.

    To test whether get_envs_dir raises correctly.
    """

    fake_home: pathlib.Path = tmp_path_factory.mktemp("home")

    return fake_home


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

    projects_dir: pathlib.Path = tmp_path_factory.mktemp("projects")

    for project_name in project_names:
        project_path = projects_dir.joinpath(project_name)
        project_path.mkdir()

    return projects_dir


@pytest.fixture
def empty_projects_dir(tmp_path_factory):
    """
    Returns a fake projects directory with no projects inside it.
    """

    projects_dir: pathlib.Path = tmp_path_factory.mktemp("projects")

    return projects_dir
