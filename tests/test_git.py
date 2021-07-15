"""
Tests for the git module.

Author: Tom Fleet
Created: 19/06/2021
"""

import shutil
import subprocess
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


def test_raise_for_git_raises_if_git_is_none():

    git = Git(git=None)

    with pytest.raises(GitNotInstalledError):
        git.raise_for_git()


def test_run_passes_correct_command_to_subprocess(mocker: MockerFixture):

    # Make sure it doesn't actually try and run anything
    # give it a fake executable
    git = Git(git="testgit")

    # Mock the subprocess of calling git
    mock_subprocess = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git.run("some", "random", "git", "args", "--flag", check=True, cwd=Path("some/dir"))

    mock_subprocess.assert_called_once_with(
        [
            "testgit",
            "some",
            "random",
            "git",
            "args",
            "--flag",
        ],
        cwd=Path("some/dir"),
        check=True,
    )


def test_run_raises_on_subprocess_error(mocker: MockerFixture):

    git = Git(git="testgit")

    # Mock the subprocess of calling git, but have it raise an error
    mocker.patch(
        "pytoil.git.git.subprocess.run",
        autospec=True,
        side_effect=[subprocess.CalledProcessError(-1, "cmd")],
    )

    with pytest.raises(subprocess.CalledProcessError):
        git.run("some", "silly", "git", "args", check=True, cwd=Path("somewhere/else"))


def test_clone_passes_correct_command_to_subprocess(mocker: MockerFixture):

    # Make sure it doesn't actually try and run anything
    # give it a fake executable
    git = Git(git="testgit")

    # Mock the subprocess of calling git
    mock_subprocess = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git.clone(url="https://testhub.com/fake/repo.git", check=True, cwd=Path("some/dir"))

    mock_subprocess.assert_called_once_with(
        ["testgit", "clone", "https://testhub.com/fake/repo.git"],
        cwd=Path("some/dir"),
        check=True,
    )


def test_init_passes_correct_command_to_subprocess(mocker: MockerFixture):

    # Make sure it doesn't actually try and run anything
    # give it a fake executable
    git = Git(git="testgit")

    # Mock the subprocess of calling git
    mock_subprocess = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git.init(path=Path("some/dir/project"), check=True)

    mock_subprocess.assert_called_once_with(
        ["testgit", "init"],
        cwd=Path("some/dir/project"),
        check=True,
    )


def test_set_upstream_passes_correct_command_to_subprocess(mocker: MockerFixture):

    git = Git(git="testgit")

    mock_subprocess = mocker.patch("pytoil.git.git.subprocess.run", autospec=True)

    git.set_upstream(
        owner="someone", repo="project", path=Path("some/dir/project"), check=True
    )

    mock_subprocess.assert_called_once_with(
        [
            "testgit",
            "remote",
            "add",
            "upstream",
            "https://github.com/someone/project.git",
        ],
        check=True,
        cwd=Path("some/dir/project"),
    )
