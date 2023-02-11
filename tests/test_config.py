from __future__ import annotations

import os
import platform
import tempfile
from pathlib import Path

import pytest
from pytoil.config import Config, defaults

# GitHub Actions
ON_CI = bool(os.getenv("CI"))
ON_WINDOWS = platform.system().lower() == "windows"


def test_config_init_defaults() -> None:
    config = Config()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == defaults.TOKEN
    assert config.username == defaults.USERNAME
    assert config.editor == defaults.EDITOR
    assert config.conda_bin == defaults.CONDA_BIN
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.git == defaults.GIT


def test_config_init_passed() -> None:
    config = Config(
        projects_dir=Path("some/dir"),
        token="sometoken",
        username="me",
        editor="fakeedit",
        conda_bin="mamba",
        common_packages=["black", "mypy", "flake8"],
        git=False,
    )

    assert config.projects_dir == Path("some/dir")
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.editor == "fakeedit"
    assert config.conda_bin == "mamba"
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.git is False


def test_config_helper() -> None:
    config = Config.helper()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == "Put your GitHub personal access token here"
    assert config.username == "This your GitHub username"
    assert config.editor == defaults.EDITOR
    assert config.conda_bin == defaults.CONDA_BIN
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.git == defaults.GIT


def test_config_load() -> None:
    with tempfile.NamedTemporaryFile("w", delete=not (ON_CI and ON_WINDOWS)) as file:
        # Make a fake config object
        config = Config(
            projects_dir=Path("~/some/dir"),
            token="sometoken",
            username="me",
            editor="fakeedit",
            common_packages=["black", "mypy", "flake8"],
            git=False,
        )

        # Write the config
        config.write(path=Path(file.name))

        # Load the config
        loaded_config = Config.load(path=Path(file.name))

    assert loaded_config.projects_dir == Path("~/some/dir").expanduser()
    assert loaded_config.token == "sometoken"
    assert loaded_config.username == "me"
    assert loaded_config.editor == "fakeedit"
    assert loaded_config.common_packages == ["black", "mypy", "flake8"]
    assert loaded_config.git is False


@pytest.mark.parametrize(
    ("editor", "want"),
    [
        ("code", True),
        ("", True),  # Because it will default to $EDITOR
        ("None", False),
        ("none", False),
    ],
)
def test_specifies_editor(editor: str, want: bool) -> None:
    config = Config(editor=editor)
    assert config.specifies_editor() is want


def test_from_file_raises_on_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        Config.load(path=Path("not/here.toml"))


@pytest.mark.parametrize(
    ("username", "token", "expected"),
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
def test_can_use_api(username: str, token: str, expected: bool) -> None:
    config = Config(username=username, token=token)

    assert config.can_use_api() is expected


def test_file_write() -> None:
    with tempfile.NamedTemporaryFile("w", delete=not (ON_CI and ON_WINDOWS)) as file:
        # Make a fake config object
        config = Config(
            projects_dir=Path("some/dir").expanduser().resolve(),
            token="sometoken",
            username="me",
            editor="fakeedit",
            common_packages=["black", "mypy", "flake8"],
            git=False,
        )

        # Write the config
        config.write(path=Path(file.name))

        file_config = Config.load(Path(file.name))

        assert file_config == config
