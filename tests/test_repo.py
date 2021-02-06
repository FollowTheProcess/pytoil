"""
Tests for the repo module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib
import urllib.error

import pytest

import pytoil
from pytoil.repo import Repo


def test_repo_init():

    repo = Repo(owner="me", name="myproject")

    assert repo.owner == "me"
    assert repo.name == "myproject"
    assert repo.url == "https://github.com/me/myproject.git"
    assert repo.path is None


def test_repo_init_defaults(mocker, temp_config_file):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # name is required
        repo = Repo(name="diffproject")

        assert repo.owner == "tempfileuser"
        assert repo.name == "diffproject"
        assert repo.url == "https://github.com/tempfileuser/diffproject.git"
        assert repo.path is None


def test_repo_repr():

    repo = Repo(owner="me", name="myproject")

    assert repo.__repr__() == "Repo(owner='me', name='myproject')"


def test_repo_setters():

    repo = Repo(owner="me", name="myproject")

    # Assert values before
    assert repo.url == "https://github.com/me/myproject.git"
    assert repo.path is None

    # Set the values
    # repo.url is read only
    repo.path = pathlib.Path("fake/local/path/myproject")

    # Assert values after
    assert repo.url == "https://github.com/me/myproject.git"
    assert repo.path == pathlib.Path("fake/local/path/myproject")


@pytest.mark.parametrize(
    "path, exists",
    [(pathlib.Path(__file__), True), (pathlib.Path("missing/file"), False)],
)
def test_repo_exists_local_returns_correct_exist(mocker, path, exists):

    # Swap out the Repo.path property for the path in parametrize
    with mocker.patch.object(pytoil.repo.Repo, "path", path):

        repo = Repo(owner="me", name="myproject")

        assert repo.exists_local() is exists


def test_repo_exists_local_handles_none_correctly():

    repo = Repo(owner="me", name="myproject")

    # repo.path is None by default
    assert repo.path is None
    assert repo.exists_local() is False


def test_repo_exists_remote_returns_false_on_missing_repo(mocker, temp_config_file):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # Patch out urllib.request.urllopen to always raise a 404 not found
        # which is our indication in `exists_remote` that the repo doesn't exist
        mocker.patch(
            "pytoil.api.urllib.request.urlopen",
            autospec=True,
            side_effect=urllib.error.HTTPError(
                "https://api.github.com/not/here",
                404,
                "Not Found",
                {"header": "yes"},
                None,
            ),
        )

        # Rest of the params will be filled in by our patched config file
        repo = Repo(name="missingproject")

        assert repo.exists_remote() is False


def test_repo_exists_remote_returns_true_on_valid_repo(mocker, temp_config_file):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # Now patch out API.get_repo to return some arbitrary dict
        # Indication that everything worked okay
        mocker.patch(
            "pytoil.api.API.get_repo",
            autospec=True,
            return_value={"repo": "yes", "name": "myproject"},
        )

        repo = Repo(name="myproject")

        assert repo.exists_remote() is True


@pytest.mark.parametrize(
    "error_code, message",
    [
        (400, "Bad Request"),
        (401, "Unauthorized"),
        (408, "Request Timeout"),
        (502, "Bad Gateway"),
        (500, "Internal Server Error"),
    ],
)
def test_repo_exists_remote_raises_on_other_http_error(
    mocker, temp_config_file, error_code, message
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.Config, "CONFIG_PATH", temp_config_file):

        # Patch out urllib.request.urlopen to raise
        # other HTTP errors from our parametrize
        mocker.patch(
            "pytoil.api.urllib.request.urlopen",
            autospec=True,
            side_effect=urllib.error.HTTPError(
                "https://api.nothub.com/not/here",
                error_code,
                message,
                {"header": "yes"},
                None,
            ),
        )

        repo = Repo(name="myproject")

        with pytest.raises(urllib.error.HTTPError):
            repo.exists_remote()
