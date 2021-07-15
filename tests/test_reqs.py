"""
Tests for the RequirementsTxtEnv class.

Author: Tom Fleet
Created: 15/07/2021
"""

from pathlib import Path

from pytest_mock import MockerFixture

from pytoil.environments import ReqTxtEnv


def test_reqenv_init():

    root = Path("/Users/me/fakeproject")
    venv = ReqTxtEnv(project_path=root)

    assert venv.project_path == root
    assert venv.executable == root.joinpath(".venv/bin/python")


def test_reqenv_repr():

    root = Path("/Users/me/fakeproject")
    venv = ReqTxtEnv(project_path=root)

    assert repr(venv) == f"ReqTxtEnv(project_path={root!r})"


def test_reqenv_info_name():

    root = Path("/Users/me/fakeproject")
    venv = ReqTxtEnv(project_path=root)

    assert venv.info_name == "requirements file"


def test_executable_points_to_correct_path():

    root = Path("/Users/me/fakeproject")
    venv = ReqTxtEnv(project_path=root)

    assert venv.executable == root.joinpath(".venv/bin/python")


def test_install_self_passes_correct_command_to_subprocess_dev_txt(
    mocker: MockerFixture, requirements_dev_project
):

    root = requirements_dev_project
    venv = ReqTxtEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.reqs.subprocess.run", autospec=True
    )

    # Make it think the venv exists already
    mocker.patch(
        "pytoil.environments.reqs.ReqTxtEnv.exists", autospec=True, return_value=True
    )

    venv.install_self()

    mock_subprocess.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "-r",
            "requirements_dev.txt",
            "--quiet",
        ],
        check=True,
        cwd=root,
    )


def test_install_self_passes_correct_command_to_subprocess_req_txt(
    mocker: MockerFixture, requirements_project
):

    root = requirements_project
    venv = ReqTxtEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.reqs.subprocess.run", autospec=True
    )

    # Make it think the venv exists already
    mocker.patch(
        "pytoil.environments.reqs.ReqTxtEnv.exists", autospec=True, return_value=True
    )

    venv.install_self()

    mock_subprocess.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "--quiet",
        ],
        check=True,
        cwd=root,
    )


def test_install_self_creates_environment_if_doesnt_exist_first_req_txt(
    mocker: MockerFixture, requirements_project
):

    root = requirements_project
    venv = ReqTxtEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.reqs.subprocess.run", autospec=True
    )

    # Make it think the venv doesn't exist
    mocker.patch(
        "pytoil.environments.reqs.ReqTxtEnv.exists", autospec=True, return_value=False
    )

    mock_create = mocker.patch(
        "pytoil.environments.reqs.ReqTxtEnv.create", autospec=True
    )

    venv.install_self()

    mock_create.assert_called_once()

    mock_subprocess.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "--quiet",
        ],
        check=True,
        cwd=root,
    )


def test_install_self_creates_environment_if_doesnt_exist_first_dev_txt(
    mocker: MockerFixture, requirements_dev_project
):

    root = requirements_dev_project
    venv = ReqTxtEnv(project_path=root)

    mock_subprocess = mocker.patch(
        "pytoil.environments.reqs.subprocess.run", autospec=True
    )

    # Make it think the venv doesn't exist
    mocker.patch(
        "pytoil.environments.reqs.ReqTxtEnv.exists", autospec=True, return_value=False
    )

    mock_create = mocker.patch(
        "pytoil.environments.reqs.ReqTxtEnv.create", autospec=True
    )

    venv.install_self()

    mock_create.assert_called_once()

    mock_subprocess.assert_called_once_with(
        [
            f"{venv.executable}",
            "-m",
            "pip",
            "install",
            "-r",
            "requirements_dev.txt",
            "--quiet",
        ],
        check=True,
        cwd=root,
    )
