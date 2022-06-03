from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.environments.flit import Flit
from pytoil.exceptions import FlitNotInstalledError


def test_flit():
    flit = Flit(root=Path("somewhere"), flit="notflit")

    assert flit.project_path == Path("somewhere").resolve()
    assert flit.name == "flit"
    assert flit.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")
    assert flit.flit == "notflit"


def test_flit_repr():
    flit = Flit(root=Path("somewhere"), flit="notflit")
    assert repr(flit) == f"Flit(root={Path('somewhere')!r}, flit='notflit')"


def test_raises_if_flit_not_installed():
    flit = Flit(root=Path("somewhere"), flit=None)

    with pytest.raises(FlitNotInstalledError):
        flit.install_self()


@pytest.mark.parametrize(
    "silent, stdout, stderr",
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_venv_exists(mocker: MockerFixture, silent: bool, stdout, stderr):
    mocker.patch(
        "pytoil.environments.flit.Flit.exists",
        autospec=True,
        return_value=True,
    )

    mock = mocker.patch("pytoil.environments.flit.subprocess.run", autospec=True)

    env = Flit(root=Path("somewhere"), flit="notflit")

    env.install_self(silent=silent)

    mock.assert_called_once_with(
        [
            "notflit",
            "install",
            "--deps",
            "develop",
            "--symlink",
            "--python",
            f"{env.executable}",
        ],
        cwd=env.project_path,
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
def test_install_self_venv_doesnt_exist(
    mocker: MockerFixture, silent: bool, stdout, stderr
):
    mocker.patch(
        "pytoil.environments.flit.Flit.exists",
        autospec=True,
        return_value=False,
    )

    mock_create = mocker.patch("pytoil.environments.flit.Flit.create", autospec=True)

    mock = mocker.patch("pytoil.environments.flit.subprocess.run", autospec=True)

    env = Flit(root=Path("somewhere"), flit="notflit")

    env.install_self(silent=silent)

    mock_create.assert_called_once()

    mock.assert_called_once_with(
        [
            "notflit",
            "install",
            "--deps",
            "develop",
            "--symlink",
            "--python",
            f"{env.executable}",
        ],
        cwd=env.project_path,
        stdout=stdout,
        stderr=stderr,
    )
