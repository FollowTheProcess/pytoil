"""
Tests for the config module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib

import pytest
from pytest_mock import MockerFixture

import pytoil
from pytoil.config import DEFAULT_PROJECTS_DIR, Config
from pytoil.exceptions import InvalidConfigError


def test_config_init_default():

    config = Config()

    assert config.username == "UNSET"
    assert config.token == "UNSET"
    # Default development path
    assert config.projects_dir == DEFAULT_PROJECTS_DIR
    assert config.vscode is False


def test_config_init_passed():

    config = Config(
        username="me",
        token="definitelynotatoken",
        projects_dir=pathlib.Path("/Users/me/projects"),
        vscode=True,
    )

    assert config.username == "me"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == pathlib.Path("/Users/me/projects")
    assert config.vscode is True


def test_config_init_username():

    config = Config(username="me")

    assert config.username == "me"
    assert config.token == "UNSET"
    assert config.projects_dir == DEFAULT_PROJECTS_DIR
    assert config.vscode is False


def test_config_init_token():

    config = Config(token="definitelynotatoken")

    assert config.username == "UNSET"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == DEFAULT_PROJECTS_DIR
    assert config.vscode is False


def test_config_init_projects_dir():

    config = Config(projects_dir=pathlib.Path("/Users/madeup/path"))

    assert config.username == "UNSET"
    assert config.token == "UNSET"
    assert config.projects_dir == pathlib.Path("/Users/madeup/path")
    assert config.vscode is False


def test_config_init_vscode():

    config = Config(vscode=True)

    assert config.username == "UNSET"
    assert config.token == "UNSET"
    assert config.projects_dir == DEFAULT_PROJECTS_DIR
    assert config.vscode is True


def test_config_repr_default():

    config = Config()

    assert (
        config.__repr__()
        == "Config(username='UNSET', "
        + "token='UNSET', "
        + f"projects_dir={DEFAULT_PROJECTS_DIR!r}, "
        + "vscode=False, "
        + "common_packages=None)"
    )


def test_config_repr_passed():

    path = pathlib.Path("/Users/me/projects")

    config = Config(
        username="me",
        token="definitelynotatoken",
        projects_dir=path,
        vscode=True,
        common_packages=["black", "flake8", "mypy"],
    )

    expected = (
        "Config(username='me', "
        + "token='definitelynotatoken', "
        + f"projects_dir={path!r}, "
        + "vscode=True, "
        + "common_packages=['black', 'flake8', 'mypy'])"
    )

    assert config.__repr__() == expected


def test_config_dict_default():

    config = Config()

    assert config.__dict__ == {
        "username": "UNSET",
        "token": "UNSET",
        "projects_dir": DEFAULT_PROJECTS_DIR,
        "vscode": False,
        "common_packages": None,
    }


def test_config_dict_passed():

    path = pathlib.Path("/Users/me/projects")

    config = Config(
        username="me",
        token="definitelynotatoken",
        projects_dir=path,
        vscode=True,
        common_packages=["black", "flake8", "mypy"],
    )

    assert config.__dict__ == {
        "username": "me",
        "token": "definitelynotatoken",
        "projects_dir": path,
        "vscode": True,
        "common_packages": ["black", "flake8", "mypy"],
    }


def test_config_setters():

    config = Config()

    # Assert before
    assert config.username == "UNSET"
    assert config.token == "UNSET"
    assert config.projects_dir == DEFAULT_PROJECTS_DIR
    assert config.vscode is False

    # Change value using setters
    config.username = "me"
    config.token = "definitelynotatoken"
    config.projects_dir = pathlib.Path("/Users/me/projects")
    config.vscode = True

    # Assert after
    assert config.username == "me"
    assert config.token == "definitelynotatoken"
    assert config.projects_dir == pathlib.Path("/Users/me/projects")
    assert config.vscode is True


def test_config_get_good_file(temp_config_file, mocker: MockerFixture):
    """
    Tests config.get on a file with valid key value pairs.
    """
    # Patch out the default pointer to the config file for our temp fixture
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        config = Config.get()

        assert config.username == "tempfileuser"
        assert config.token == "tempfiletoken"
        assert config.projects_dir == pathlib.Path("/Users/tempfileuser/projects")
        assert config.vscode is True


def test_config_get_raises_on_missing_file(mocker: MockerFixture):
    """
    Tests config.get raises the correct exception if the config
    file is missing.
    """

    with mocker.patch.object(
        pytoil.config.config,
        "CONFIG_PATH",
        pathlib.Path("definitely/not/here/.pytoil.yml"),
    ):

        with pytest.raises(FileNotFoundError):
            Config.get()


@pytest.mark.parametrize(
    "name, token, projects_dir, vscode, common_packages, expected_dict",
    [
        (
            "me",
            "sillytoken",
            pathlib.Path("/Users/me/projects"),
            True,
            ["black", "flake8", "mypy"],
            {
                "username": "me",
                "token": "sillytoken",
                "projects_dir": "/Users/me/projects",
                "vscode": True,
                "common_packages": ["black", "flake8", "mypy"],
            },
        ),
        (
            "someguy",
            "loltoken",
            pathlib.Path("/Users/someguy/dingleprojects"),
            False,
            None,
            {
                "username": "someguy",
                "token": "loltoken",
                "projects_dir": "/Users/someguy/dingleprojects",
                "vscode": False,
                "common_packages": None,
            },
        ),
        (
            "dave",
            "hahahatoken",
            pathlib.Path("/Users/dave/hahaprojects"),
            True,
            ["pylint", "autopep8", "pytest"],
            {
                "username": "dave",
                "token": "hahahatoken",
                "projects_dir": "/Users/dave/hahaprojects",
                "vscode": True,
                "common_packages": ["pylint", "autopep8", "pytest"],
            },
        ),
    ],
)
def test_config_to_dict_returns_correct_values(
    name, token, projects_dir, vscode, common_packages, expected_dict
):

    config = Config(
        username=name,
        token=token,
        projects_dir=projects_dir,
        vscode=vscode,
        common_packages=common_packages,
    )

    assert config.to_dict() == expected_dict


def test_config_validate_raises_on_unset_username():

    config = Config(
        username="UNSET", token="definitelynotatoken", projects_dir="/Users/me/projects"
    )

    with pytest.raises(InvalidConfigError):
        config.validate()


def test_config_raise_if_unset_raises_on_unset_token():

    config = Config(username="me", token="UNSET", projects_dir="/Users/me/projects")

    with pytest.raises(InvalidConfigError):
        config.validate()


def test_config_show_outputs_correct_text(capsys):

    config = Config(
        username="me",
        token="UNSET",
        projects_dir=pathlib.Path("/Users/me/projects"),
        vscode=True,
        common_packages=["black", "flake8", "mypy"],
    )

    config.show()

    captured = capsys.readouterr()

    expected_output: str = (
        "username: 'me'\n"
        + "token: 'UNSET'\n"
        + "projects_dir: '/Users/me/projects'\n"
        + "vscode: True\n"
        + "common_packages: ['black', 'flake8', 'mypy']\n"
    )

    assert captured.out == expected_output


def test_config_write(mocker: MockerFixture, temp_config_file):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        original_config = Config.get()

        # Check config values before change
        assert original_config.username == "tempfileuser"
        assert original_config.token == "tempfiletoken"
        assert original_config.projects_dir == pathlib.Path(
            "/Users/tempfileuser/projects"
        )
        assert original_config.vscode is True

        config = Config(
            username="me",
            token="definitelynotatoken",
            projects_dir=pathlib.Path("/Users/me/projects"),
            vscode=False,
        )

        # Write these new attributes to the temp config file (overwriting)
        config.write()

        # Check config values after change

        new_config = Config.get()

        assert new_config.username == "me"
        assert new_config.token == "definitelynotatoken"
        assert new_config.projects_dir == pathlib.Path("/Users/me/projects")
        assert new_config.vscode is False
