from __future__ import annotations

import shutil
import subprocess
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


def test_git_repr():
    git = Git(git="hellogit")

    assert repr(git) == "Git(git='hellogit')"


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_git_init(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git = Git(git="notgit")

    git.init(Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        ["notgit", "init"],
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_git_clone(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git = Git(git="notgit")

    git.clone(
        url="https://nothub.com/some/project.git", cwd=Path("somewhere"), silent=silent
    )

    mock.assert_called_once_with(
        ["notgit", "clone", "https://nothub.com/some/project.git"],
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


def test_instantiation_raises_if_git_not_insalled():
    with pytest.raises(GitNotInstalledError):
        Git(git=None)


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_git_set_upstream(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git = Git(git="notgit")

    git.set_upstream(owner="me", repo="project", cwd=Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        ["notgit", "remote", "add", "upstream", "https://github.com/me/project.git"],
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_git_add_all(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git = Git(git="notgit")

    git.add(cwd=Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        ["notgit", "add", "-A"], cwd=Path("somewhere"), stdout=stdout, stderr=stderr
    )


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_git_commit(mocker: MockerFixture, silent: bool, stdout, stderr):
    mock = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git = Git(git="notgit")

    git.commit(message="Commit message", cwd=Path("somewhere"), silent=silent)

    mock.assert_called_once_with(
        ["notgit", "commit", "-m", "Commit message"],
        cwd=Path("somewhere"),
        stdout=stdout,
        stderr=stderr,
    )
