import asyncio
import shutil
import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import GitNotInstalledError
from pytoil.git import Git


def test_git_instanciation_default():

    git = Git()

    assert git.git == shutil.which("git")


def test_git_instanciation_passed():

    git = Git(git="/some/path/to/git")

    assert git.git == "/some/path/to/git"


def test_git_instanciation_none():

    # You'd never do this but if a user does not have
    # git installed `shutil.which` will return None
    git = Git(git=None)

    assert git.git is None


def test_git_repr():

    git = Git(git="hellogit")

    assert repr(git) == "Git(git='hellogit')"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_git_init(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git="notgit")

    await git.init(Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        "notgit",
        "init",
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_git_init_raises_if_git_not_installed(mocker: MockerFixture):
    mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git=None)

    with pytest.raises(GitNotInstalledError):
        await git.init(Path("somewhere"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_git_clone(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git="notgit")

    await git.clone(
        url="https://nothub.com/some/project.git", cwd=Path("somewhere"), silent=silent
    )

    mock.assert_called_once_with(
        "notgit",
        "clone",
        "https://nothub.com/some/project.git",
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_git_clone_raises_if_git_not_installed(mocker: MockerFixture):
    mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git=None)

    with pytest.raises(GitNotInstalledError):
        await git.clone(url="https://nothub.com/me/project.git", cwd=Path("somewhere"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_git_set_upstream(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git="notgit")

    await git.set_upstream(
        owner="me", repo="project", cwd=Path("somewhere"), silent=silent
    )

    mock.assert_called_once_with(
        "notgit",
        "remote",
        "add",
        "upstream",
        "https://github.com/me/project.git",
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_git_set_upstream_raises_if_git_not_installed(mocker: MockerFixture):
    mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git=None)

    with pytest.raises(GitNotInstalledError):
        await git.set_upstream(owner="me", repo="project", cwd=Path("here"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_git_add_all(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git="notgit")

    await git.add(cwd=Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        "notgit", "add", "-A", cwd=Path("somewhere"), stdout=stdout, stderr=stderr
    )


@pytest.mark.asyncio
async def test_git_add_raises_if_git_not_installed(mocker: MockerFixture):
    mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git=None)

    with pytest.raises(GitNotInstalledError):
        await git.add(cwd=Path("somewhere"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
async def test_git_commit(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git="notgit")

    await git.commit(message="Commit message", cwd=Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        "notgit",
        "commit",
        "-m",
        "Commit message",
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.asyncio
async def test_git_commit_raises_if_git_not_installed(mocker: MockerFixture):
    mocker.patch("pytoil.git.git.asyncio.create_subprocess_exec", autospec=True)

    git = Git(git=None)

    with pytest.raises(GitNotInstalledError):
        await git.commit(cwd=Path("somewhere"))
