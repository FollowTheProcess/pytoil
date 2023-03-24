from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TextIO

import pytest
from pytest_mock import MockerFixture
from pytoil.environments import Requirements


def test_requirements() -> None:
    env = Requirements(root=Path("somewhere"))

    assert env.project_path == Path("somewhere").resolve()
    assert env.name == "requirements file"
    assert env.executable == Path("somewhere").resolve().joinpath(".venv/bin/python")


def test_requirements_repr() -> None:
    env = Requirements(root=Path("somewhere"))
    assert repr(env) == f"Requirements(root={Path('somewhere')!r})"


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_venv_exists(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mocker.patch(
        "pytoil.environments.reqs.Requirements.exists",
        autospec=True,
        return_value=True,
    )

    mock = mocker.patch("pytoil.environments.reqs.subprocess.run", autospec=True)

    env = Requirements(root=Path("somewhere"))

    env.install_self(silent=silent)

    mock.assert_called_once_with(
        [f"{env.executable}", "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=env.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_venv_doesnt_exist(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    mocker.patch(
        "pytoil.environments.reqs.Requirements.exists",
        autospec=True,
        return_value=False,
    )

    mock = mocker.patch("pytoil.environments.reqs.subprocess.run", autospec=True)

    mock_create = mocker.patch(
        "pytoil.environments.reqs.Requirements.create", autospec=True
    )

    env = Requirements(root=Path("somewhere"))

    env.install_self(silent=silent)

    mock_create.assert_called_once()

    mock.assert_called_once_with(
        [f"{env.executable}", "-m", "pip", "install", "-r", "requirements.txt"],
        cwd=env.project_path,
        stdout=stdout,
        stderr=stderr,
    )


@pytest.mark.parametrize(
    ("silent", "stdout", "stderr"),
    [
        (True, subprocess.DEVNULL, subprocess.DEVNULL),
        (False, sys.stdout, sys.stderr),
    ],
)
def test_install_self_requirements_dev(
    mocker: MockerFixture, silent: bool, stdout: TextIO | int, stderr: TextIO | int
) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "requirements-dev.txt").touch()

        mocker.patch(
            "pytoil.environments.reqs.Requirements.exists",
            autospec=True,
            return_value=True,
        )

        mock = mocker.patch("pytoil.environments.reqs.subprocess.run", autospec=True)

        env = Requirements(root=Path(tmpdir))

        env.install_self(silent=silent)

        mock.assert_called_once_with(
            [f"{env.executable}", "-m", "pip", "install", "-r", "requirements-dev.txt"],
            cwd=env.project_path,
            stdout=stdout,
            stderr=stderr,
        )
