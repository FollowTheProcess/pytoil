"""
Tests for the config module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib

import pytest

import pytoil
from pytoil.config import DEFAULT_PROJECTS_DIR, Config
from pytoil.exceptions import InvalidConfigError


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


def test_config_raise_if_unset_raises_on_unset_username():

    config = Config(
        username="UNSET", token="definitelynotatoken", projects_dir="/Users/me/projects"
    )

    with pytest.raises(InvalidConfigError):
        config.raise_if_unset()


def test_config_raise_if_unset_raises_on_unset_token():

    config = Config(username="me", token="UNSET", projects_dir="/Users/me/projects")

    with pytest.raises(InvalidConfigError):
        config.raise_if_unset()


def test_config_show_outputs_correct_text(capsys):

    config = Config(username="me", token="UNSET", projects_dir="/Users/me/projects")

    config.show()

    captured = capsys.readouterr()

    expected_output: str = (
        "\nusername: 'me'\n\ntoken: 'UNSET'\n\nprojects_dir: '/Users/me/projects'\n\n"
    )

    assert captured.out == expected_output


def test_config_write(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        original_config = Config.get()

        # Check config values before change
        assert original_config.username == "tempfileuser"
        assert original_config.token == "tempfiletoken"
        assert original_config.projects_dir == pathlib.Path(
            "/Users/tempfileuser/projects"
        )

        config = Config(
            username="me",
            token="definitelynotatoken",
            projects_dir="/Users/me/projects",
        )

        # Write these new attributes to the temp config file (overwriting)
        config.write()

        # Check config values after change

        new_config = Config.get()

        assert new_config.username == "me"
        assert new_config.token == "definitelynotatoken"
        assert new_config.projects_dir == pathlib.Path("/Users/me/projects")
