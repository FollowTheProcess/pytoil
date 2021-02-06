"""
Tests for the config module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib

import pytest

import pytoil
from pytoil.config import Config


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


def test_config_interprets_missing_keys_as_none(mocker, temp_config_file_missing_key):
    """
    Checks that if a key is missing from the yml file, the object is still
    instantiated, but with None as the keys value.
    """

    with mocker.patch.object(
        pytoil.config.Config, "CONFIG_PATH", temp_config_file_missing_key
    ):
        config = Config.get()

    assert config.username == "tempfileuser"
    # token is missing in the temp file
    assert config.token is None
    assert config.projects_dir == pathlib.Path("Users/tempfileuser/projects")


def test_config_interprets_blank_value_as_none(
    mocker, temp_config_file_key_with_blank_value
):
    """
    Checks that if a key is present in the yml file, but it's value is blank. This
    is also treated as None.
    """

    with mocker.patch.object(
        pytoil.config.Config, "CONFIG_PATH", temp_config_file_key_with_blank_value
    ):
        config = Config.get()

    assert config.username == "tempfileuser"
    # token key is present but value is blank
    assert config.token is None
    assert config.projects_dir == pathlib.Path("Users/tempfileuser/projects")


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
