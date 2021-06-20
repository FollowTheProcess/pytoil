"""
Tests for the config module.

Author: Tom Fleet
Created: 18/06/2021
"""

from pathlib import Path

import pytest

from pytoil.config import Config, defaults

TESTDATA = Path(__file__).parent.joinpath("testdata").resolve()
TEST_CONFIG_FILE = TESTDATA / ".pytoil.yml"


def test_config_init_defaults():

    config = Config()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == defaults.TOKEN
    assert config.username == defaults.USERNAME
    assert config.vscode == defaults.VSCODE
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.init_on_new == defaults.INIT_ON_NEW


def test_config_init_passed():

    config = Config(
        projects_dir=Path("some/dir"),
        token="sometoken",
        username="me",
        vscode=True,
        common_packages=["black", "mypy", "flake8"],
        init_on_new=False,
    )

    assert config.projects_dir == Path("some/dir")
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.vscode is True
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.init_on_new is False


def test_config_helper():

    config = Config.helper()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == "Put your GitHub personal access token here"
    assert config.username == "This your GitHub username"
    assert config.vscode == defaults.VSCODE
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.init_on_new == defaults.INIT_ON_NEW


def test_from_file():

    config = Config.from_file(path=TEST_CONFIG_FILE)

    assert config.projects_dir == Path("/Users/me/Projects")
    assert config.token == "ljsakdhka2387gi1hdbqw87"
    assert config.username == "FollowTheProcess"
    assert config.vscode is True
    assert config.common_packages == ["black", "flake8", "mypy", "isort"]
    assert config.init_on_new is True


def test_from_file_raises_on_missing_file():

    with pytest.raises(FileNotFoundError):
        Config.from_file(path=Path("not/here.yml"))


def test_from_dict():

    config_dict = {
        "projects_dir": "some/dir",
        "token": "sometoken",
        "username": "me",
        "vscode": True,
        "common_packages": ["black", "mypy", "flake8"],
        "init_on_new": False,
    }

    config = Config.from_dict(config_dict)

    assert config.projects_dir == Path("some/dir")
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.vscode is True
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.init_on_new is False


def test_from_dict_wrong_types():
    """
    Tests that even if everything is brought in as a string
    the types of the config all get handled under the hood.

    Thanks pydantic!
    """

    config_dict = {
        "projects_dir": "some/dir",
        "token": "sometoken",
        "username": "me",
        "vscode": "True",
        "common_packages": ["black", "mypy", "flake8"],
        "init_on_new": "False",
    }

    config = Config.from_dict(config_dict)

    assert config.projects_dir == Path("some/dir")
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.vscode is True
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.init_on_new is False


def test_from_dict_some_missing():
    """
    Tests that even if we pass a partial dict, the default values
    will be used for the missing bits.
    """

    config_dict = {
        "token": "sometoken",
        "username": "me",
        "common_packages": ["black", "mypy", "flake8"],
    }

    config = Config.from_dict(config_dict)

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.vscode is defaults.VSCODE
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.init_on_new is defaults.INIT_ON_NEW


def test_to_dict():

    config = Config.from_file(path=TEST_CONFIG_FILE)

    config_dict = config.to_dict()

    assert config_dict["projects_dir"] == "/Users/me/Projects"
    assert config_dict["token"] == "ljsakdhka2387gi1hdbqw87"
    assert config_dict["username"] == "FollowTheProcess"
    assert config_dict["vscode"] is True
    assert config_dict["common_packages"] == ["black", "flake8", "mypy", "isort"]
    assert config_dict["init_on_new"] is True


@pytest.mark.parametrize(
    "username, token, expected",
    [
        ("", "", False),
        ("", "something", False),
        ("something", "", False),
        (
            "This your GitHub username",
            "Put your GitHub personal access token here",
            False,
        ),
        ("", "Put your GitHub personal access token here", False),
        ("This your GitHub username", "", False),
        ("something", "something", True),
    ],
)
def test_can_use_api(username, token, expected):

    config = Config(username=username, token=token)

    assert config.can_use_api() is expected


class TestFileWrite:
    """
    Test Config.write will write out a config file if the file
    does not yet exist.
    """

    target_file: Path = TESTDATA / ".testtoil.yml"

    def setup_method(self):
        pass

    def test_write(self):
        # Make a fake config object
        config = Config(
            projects_dir=Path("some/dir"),
            token="sometoken",
            username="me",
            vscode=True,
            common_packages=["black", "mypy", "flake8"],
            init_on_new=False,
        )

        # Assert the file doesn't exist before
        assert self.target_file.exists() is False

        # Write the config
        config.write(path=self.target_file)

        # Make sure it was written
        assert self.target_file.exists()

        # Read the data from the file and check it's the same
        file_config = Config.from_file(self.target_file)

        assert config == file_config

    def teardown_method(self):
        # Ensure the file always gets deleted
        self.target_file.unlink(missing_ok=True)


class TestFileOverWrite:
    """
    Test Config.write will overwrite an already existing file.
    """

    target_file: Path = TESTDATA / ".testtoil.yml"

    def setup_method(self):
        # Create the file
        self.target_file.touch()

    def test_write(self):
        # Make a fake config object
        config = Config(
            projects_dir=Path("some/dir"),
            token="sometoken",
            username="me",
            vscode=True,
            common_packages=["black", "mypy", "flake8"],
            init_on_new=False,
        )

        # Assert the file already exists
        assert self.target_file.exists()

        # Write the config
        config.write(path=self.target_file)

        # Read the data from the file and check it's the same
        file_config = Config.from_file(self.target_file)

        assert config == file_config

    def teardown_method(self):
        # Ensure the file always gets deleted
        self.target_file.unlink(missing_ok=True)
