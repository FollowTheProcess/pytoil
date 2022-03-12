import os
import platform
from pathlib import Path

import aiofiles
import pytest

from pytoil.config import Config, defaults

# GitHub Actions
ON_CI = bool(os.getenv("CI"))
ON_WINDOWS = platform.system().lower() == "windows"


def test_config_init_defaults():

    config = Config()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == defaults.TOKEN
    assert config.username == defaults.USERNAME
    assert config.editor == defaults.EDITOR
    assert config.conda_bin == defaults.CONDA_BIN
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.cache_timeout == defaults.CACHE_TIMEOUT_SECS
    assert config.git == defaults.GIT


def test_config_init_passed():

    config = Config(
        projects_dir=Path("some/dir"),
        token="sometoken",
        username="me",
        editor="fakeedit",
        conda_bin="mamba",
        common_packages=["black", "mypy", "flake8"],
        cache_timeout=500,
        git=False,
    )

    assert config.projects_dir == Path("some/dir")
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.editor == "fakeedit"
    assert config.conda_bin == "mamba"
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.cache_timeout == 500
    assert config.git is False


def test_config_helper():

    config = Config.helper()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == "Put your GitHub personal access token here"
    assert config.username == "This your GitHub username"
    assert config.editor == defaults.EDITOR
    assert config.conda_bin == defaults.CONDA_BIN
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.git == defaults.GIT


@pytest.mark.parametrize(
    "editor, want",
    [
        ("code", True),
        ("", True),  # Because it will default to $EDITOR
        ("None", False),
        ("none", False),
    ],
)
def test_specifies_editor(editor: str, want: bool):

    config = Config(editor=editor)
    assert config.specifies_editor() is want


@pytest.mark.asyncio
async def test_from_file_raises_on_missing_file():

    with pytest.raises(FileNotFoundError):
        await Config.load(path=Path("not/here.toml"))


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


@pytest.mark.asyncio
async def test_file_write():
    async with aiofiles.tempfile.NamedTemporaryFile(
        "w", delete=False if ON_CI and ON_WINDOWS else True
    ) as file:
        # Make a fake config object
        config = Config(
            projects_dir=Path("some/dir"),
            token="sometoken",
            username="me",
            editor="fakeedit",
            common_packages=["black", "mypy", "flake8"],
            git=False,
        )

        # Write the config
        await config.write(path=file.name)

        file_config = await Config.load(file.name)

        assert file_config == config
