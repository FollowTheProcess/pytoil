"""
Tests for the config module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib

import pytest

import pytoil
from pytoil.config import Config
from pytoil.exceptions import InvalidConfigError


def test_config_init_default():

    config = Config()

    assert config.username is None
    assert config.token is None
    assert config.projects_dir is None


def test_config_init_passed():

    config = Config(
        username="me", token="definitelynotatoken", projects_dir="Users/me/projects"
    )

    assert config.username == "me"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == pathlib.Path("Users/me/projects")


def test_config_repr_default():

    config = Config()

    assert config.__repr__() == "Config(username=None, token=None, projects_dir=None)"


def test_config_repr_passed():

    config = Config(
        username="me", token="definitelynotatoken", projects_dir="Users/me/projects"
    )

    expected = (
        "Config(username='me', "
        + "token='definitelynotatoken', "
        + "projects_dir='Users/me/projects')"
    )

    assert config.__repr__() == expected


def test_config_setters():

    config = Config()

    # Assert before
    assert config.username is None
    assert config.token is None
    assert config.projects_dir is None

    # Change value using setters
    config.username = "me"
    config.token = "definitelynotatoken"
    config.projects_dir = "Users/me/projects"

    # Assert after
    assert config.username == "me"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == pathlib.Path("Users/me/projects")


def test_config_get_good_file(temp_config_file, mocker):
    """
    Tests config.get on a file with valid key value pairs.
    """
    # Patch out the default pointer to the config file for our temp fixture
    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        config = Config.get()

        assert config.username == "tempfileuser"
        assert config.token == "tempfiletoken"
        assert config.projects_dir == pathlib.Path("Users/tempfileuser/projects")


def test_config_get_raises_on_missing_file(mocker):
    """
    Tests config.get raises the correct exception if the config
    file is missing.
    """

    with mocker.patch.object(
        pytoil.config.Config,
        "CONFIG_PATH",
        pathlib.Path("definitely/not/here/.pytoil.yml"),
    ):

        with pytest.raises(FileNotFoundError):
            Config.get()


def test_config_raises_on_misspelled_key(mocker, temp_config_file_misspelled_key):
    """
    Checks that config.get will raise a TypeError when one of the keys in
    the yml file is misspelled.
    """

    with mocker.patch.object(
        pytoil.config.Config, "CONFIG_PATH", temp_config_file_misspelled_key
    ):
        with pytest.raises(TypeError):
            Config.get()


def test_config_raises_on_missing_username(mocker, temp_config_file_missing_username):

    with mocker.patch.object(
        pytoil.config.Config, "CONFIG_PATH", temp_config_file_missing_username
    ):
        with pytest.raises(InvalidConfigError):
            Config.get()


def test_config_raises_on_missing_token(mocker, temp_config_file_missing_token):

    with mocker.patch.object(
        pytoil.config.Config, "CONFIG_PATH", temp_config_file_missing_token
    ):
        with pytest.raises(InvalidConfigError):
            Config.get()


def test_config_raises_on_missing_projects_dir(
    mocker, temp_config_file_missing_projects_dir
):

    with mocker.patch.object(
        pytoil.config.Config, "CONFIG_PATH", temp_config_file_missing_projects_dir
    ):
        with pytest.raises(InvalidConfigError):
            Config.get()
