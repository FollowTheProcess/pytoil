"""
Tests for the config module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib

import pytest

import pytoil
from pytoil.config import DEFAULT_PROJECTS_DIR, Config


def test_config_init_default():

    config = Config()

    assert config.username == "UNSET"
    assert config.token == "UNSET"
    # Default development path
    assert config.projects_dir == DEFAULT_PROJECTS_DIR


def test_config_init_passed():

    config = Config(
        username="me", token="definitelynotatoken", projects_dir="/Users/me/projects"
    )

    assert config.username == "me"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == pathlib.Path("/Users/me/projects")


def test_config_init_username():

    config = Config(username="me")

    assert config.username == "me"
    assert config.token == "UNSET"
    assert config.projects_dir == DEFAULT_PROJECTS_DIR


def test_config_init_token():

    config = Config(token="definitelynotatoken")

    assert config.username == "UNSET"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == DEFAULT_PROJECTS_DIR


def test_config_init_projects_dir():

    config = Config(projects_dir="/Users/madeup/path")

    assert config.username == "UNSET"
    assert config.token == "UNSET"
    assert config.projects_dir == pathlib.Path("/Users/madeup/path")


def test_config_repr_default():

    config = Config()

    assert (
        config.__repr__()
        == "Config(username='UNSET', token='UNSET', projects_dir='UNSET')"
    )


def test_config_repr_passed():

    config = Config(
        username="me", token="definitelynotatoken", projects_dir="/Users/me/projects"
    )

    expected = (
        "Config(username='me', "
        + "token='definitelynotatoken', "
        + "projects_dir='/Users/me/projects')"
    )

    assert config.__repr__() == expected


def test_config_dict_default():

    config = Config()

    assert config.__dict__ == {
        "username": "UNSET",
        "token": "UNSET",
        "projects_dir": str(DEFAULT_PROJECTS_DIR),
    }


def test_config_dict_passed():

    config = Config(
        username="me", token="definitelynotatoken", projects_dir="/Users/me/projects"
    )

    assert config.__dict__ == {
        "username": "me",
        "token": "definitelynotatoken",
        "projects_dir": "/Users/me/projects",
    }


def test_config_setters():

    config = Config()

    # Assert before
    assert config.username == "UNSET"
    assert config.token == "UNSET"
    assert config.projects_dir == pathlib.Path.home().joinpath("Development")

    # Change value using setters
    config.username = "me"
    config.token = "definitelynotatoken"
    config.projects_dir = "/Users/me/projects"

    # Assert after
    assert config.username == "me"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == pathlib.Path("/Users/me/projects")


def test_config_get_good_file(temp_config_file, mocker):
    """
    Tests config.get on a file with valid key value pairs.
    """
    # Patch out the default pointer to the config file for our temp fixture
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        config = Config.get()

        assert config.username == "tempfileuser"
        assert config.token == "tempfiletoken"
        assert config.projects_dir == pathlib.Path("/Users/tempfileuser/projects")


def test_config_get_raises_on_missing_file(mocker):
    """
    Tests config.get raises the correct exception if the config
    file is missing.
    """

    with mocker.patch.object(
        pytoil.config, "CONFIG_PATH", pathlib.Path("definitely/not/here/.pytoil.yml")
    ):

        with pytest.raises(FileNotFoundError):
            Config.get()


def test_config_raises_on_misspelled_key(mocker, temp_config_file_misspelled_key):
    """
    Checks that config.get will raise a TypeError when one of the keys in
    the yml file is misspelled.
    """

    with mocker.patch.object(
        pytoil.config, "CONFIG_PATH", temp_config_file_misspelled_key
    ):
        with pytest.raises(TypeError):
            Config.get()


@pytest.mark.parametrize(
    "name, token, projects_dir, expected_dict",
    [
        (
            "me",
            "sillytoken",
            "/Users/me/projects",
            {
                "username": "me",
                "token": "sillytoken",
                "projects_dir": "/Users/me/projects",
            },
        ),
        (
            "someguy",
            "loltoken",
            "/Users/someguy/dingleprojects",
            {
                "username": "someguy",
                "token": "loltoken",
                "projects_dir": "/Users/someguy/dingleprojects",
            },
        ),
        (
            "dave",
            "hahahatoken",
            "/Users/dave/hahaprojects",
            {
                "username": "dave",
                "token": "hahahatoken",
                "projects_dir": "/Users/dave/hahaprojects",
            },
        ),
    ],
)
def test_config_to_dict_returns_correct_values(
    name, token, projects_dir, expected_dict
):

    config = Config(username=name, token=token, projects_dir=projects_dir)

    assert config.to_dict() == expected_dict
