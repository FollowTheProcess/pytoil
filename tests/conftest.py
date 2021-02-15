"""
pytest fixtures and other good stuff

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib
from typing import Dict, List, Union

import pytest
import yaml

from pytoil.api import APIResponse


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
    }

    with open(config_file, "w") as f:
        yaml.dump(yaml_dict, f)

    return config_file


@pytest.fixture
def fake_api_response():

    response: APIResponse = [
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
