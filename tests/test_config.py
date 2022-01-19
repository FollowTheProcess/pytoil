from pathlib import Path

import aiofiles
import pytest

from pytoil.config import Config, defaults


def test_config_init_defaults():

    config = Config()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == defaults.TOKEN
    assert config.username == defaults.USERNAME
    assert config.vscode == defaults.VSCODE
    assert config.code_bin == defaults.CODE_BIN
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.git == defaults.GIT


def test_config_init_passed():

    config = Config(
        projects_dir=Path("some/dir"),
        token="sometoken",
        username="me",
        vscode=True,
        code_bin="code-insiders",
        common_packages=["black", "mypy", "flake8"],
        git=False,
    )

    assert config.projects_dir == Path("some/dir")
    assert config.token == "sometoken"
    assert config.username == "me"
    assert config.vscode is True
    assert config.code_bin == "code-insiders"
    assert config.common_packages == ["black", "mypy", "flake8"]
    assert config.git is False


def test_config_helper():

    config = Config.helper()

    assert config.projects_dir == defaults.PROJECTS_DIR
    assert config.token == "Put your GitHub personal access token here"
    assert config.username == "This your GitHub username"
    assert config.vscode == defaults.VSCODE
    assert config.code_bin == defaults.CODE_BIN
    assert config.common_packages == defaults.COMMON_PACKAGES
    assert config.git == defaults.GIT


@pytest.mark.asyncio
async def test_from_file_raises_on_missing_file():

    with pytest.raises(FileNotFoundError):
        await Config.load(path=Path("not/here.yml"))


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
    async with aiofiles.tempfile.NamedTemporaryFile("w") as file:
        # Make a fake config object
        config = Config(
            projects_dir=Path("some/dir"),
            token="sometoken",
            username="me",
            vscode=True,
            common_packages=["black", "mypy", "flake8"],
            git=False,
        )

        # Write the config
        await config.write(path=file.name)

        file_config = await Config.load(file.name)

        assert file_config == config
