"""
Tests for the repo module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib
import subprocess

import pytest

import pytoil
from pytoil.exceptions import (
    APIRequestError,
    GitNotInstalledError,
    InvalidRepoPathError,
    InvalidURLError,
    LocalRepoExistsError,
    RepoNotFoundError,
)
from pytoil.repo import Repo


def test_repo_init(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        repo = Repo(owner="me", name="myproject")

        assert repo.owner == "me"
        assert repo.name == "myproject"
        assert repo.url == "https://github.com/me/myproject.git"
        assert repo.path == pathlib.Path("/Users/tempfileuser/projects/myproject")


def test_repo_init_defaults(mocker, temp_config_file):

    # Patch out the config path to be our temp file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # name is required
        repo = Repo(name="diffproject")

        assert repo.owner == "tempfileuser"
        assert repo.name == "diffproject"
        assert repo.url == "https://github.com/tempfileuser/diffproject.git"
        assert repo.path == pathlib.Path("/Users/tempfileuser/projects/diffproject")


def test_repo_repr(mocker, temp_config_file):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        repo = Repo(owner="me", name="myproject")

        assert repo.__repr__() == "Repo(owner='me', name='myproject')"


def test_repo_setters(mocker, temp_config_file):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        repo = Repo(name="myproject")

        # Assert values before
        assert repo.url == "https://github.com/tempfileuser/myproject.git"
        assert repo.path == pathlib.Path("/Users/tempfileuser/projects/myproject")

        # Set the values
        # repo.url is read only
        repo.path = pathlib.Path("fake/local/path/myproject")

        # Assert values after
        assert repo.url == "https://github.com/tempfileuser/myproject.git"
        assert repo.path == pathlib.Path("fake/local/path/myproject")


@pytest.mark.parametrize(
    "url, owner, name",
    [
        ("https://github.com/dingleuser/dinglerepo.git", "dingleuser", "dinglerepo"),
        (
            "https://github.com/MySuperUser/s1llypr0ject.git",
            "MySuperUser",
            "s1llypr0ject",
        ),
        (
            "https://github.com/FollowTheProcess/pytoil.git",
            "FollowTheProcess",
            "pytoil",
        ),
        ("https://github.com/W31rdUsern4m3/blah.git", "W31rdUsern4m3", "blah"),
        ("https://github.com/HelloDave/dave.git", "HelloDave", "dave"),
    ],
)
def test_repo_from_url(mocker, temp_config_file, url, owner, name):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        repo = Repo.from_url(url=url)

        assert repo.owner == owner
        assert repo.name == name

        # Make sure it reconstructs the url properly
        assert repo.url == url
        assert repo.path == pathlib.Path(f"/Users/tempfileuser/projects/{name}")


@pytest.mark.parametrize(
    "url",
    [
        "https://nothub.com/me/project.git",
        "",
        "http://github.com/me/project.git",
        "https://github.com/What5wk91yn-msbnu-t/what.git",
        "https://github.com/:::punctuation[]';]'[-=]/project.git"
        "https://github.com/doesntend/indotgit",
    ],
)
def test_repo_from_url_raises_on_bad_url(mocker, temp_config_file, url):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        with pytest.raises(InvalidURLError):
            Repo.from_url(url=url)


@pytest.mark.parametrize(
    "path, owner, name, url",
    [
        (
            "dingleuser/dinglerepo",
            "dingleuser",
            "dinglerepo",
            "https://github.com/dingleuser/dinglerepo.git",
        ),
        (
            "MySuperUser/s1llypr0ject",
            "MySuperUser",
            "s1llypr0ject",
            "https://github.com/MySuperUser/s1llypr0ject.git",
        ),
        (
            "FollowTheProcess/pytoil",
            "FollowTheProcess",
            "pytoil",
            "https://github.com/FollowTheProcess/pytoil.git",
        ),
        (
            "W31rdUsern4m3/blah",
            "W31rdUsern4m3",
            "blah",
            "https://github.com/W31rdUsern4m3/blah.git",
        ),
        (
            "HelloDave/dave",
            "HelloDave",
            "dave",
            "https://github.com/HelloDave/dave.git",
        ),
    ],
)
def test_repo_from_path(mocker, temp_config_file, path, owner, name, url):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        repo = Repo.from_path(path=path)

        assert repo.owner == owner
        assert repo.name == name

        # Make sure it reconstructs the url properly
        assert repo.url == url
        assert repo.path == pathlib.Path(f"/Users/tempfileuser/projects/{name}")


@pytest.mark.parametrize(
    "path",
    ["", "What5wk91yn-msbnu-t/what", ":::punctuation[]';]'[-=]/project"],
)
def test_repo_from_path_raises_on_bad_path(mocker, temp_config_file, path):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        with pytest.raises(InvalidRepoPathError):
            Repo.from_path(path=path)


def test_repo_exists_local_returns_true_if_path_exists(mocker, temp_config_file):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out Repo.path to something we know exists: this file
        with mocker.patch.object(pytoil.repo.Repo, "path", pathlib.Path(__file__)):

            repo = Repo(name="fakerepo")

            assert repo.exists_local() is True


def test_repo_exists_local_returns_false_if_path_doesnt_exist(mocker, temp_config_file):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out Repo.path to something we know doesn't exist
        with mocker.patch.object(pytoil.repo.Repo, "path", pathlib.Path("not/here")):

            repo = Repo(name="fakerepo")

            assert repo.exists_local() is False


@pytest.mark.parametrize(
    "non_existing_repo_name", ["noexist1", "noexist2", "noexist3", "noexist4"]
)
def test_repo_exists_remote_returns_false_on_missing_repo(
    mocker, temp_config_file, non_existing_repo_name
):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out api.get to always raise a 404 not found
        # which is our indication in `exists_remote` that the repo doesn't exist
        mocker.patch(
            "pytoil.api.API.get_repo_names",
            autospec=True,
            return_value={"exist1", "exist2", "exist3", "exist4"},
        )

        # Rest of the params will be filled in by our patched config file
        repo = Repo(name=non_existing_repo_name)

        assert repo.exists_remote() is False


@pytest.mark.parametrize("existing_repo_name", ["exist1", "exist2", "exist3", "exist4"])
def test_repo_exists_remote_returns_true_on_valid_repo(
    mocker, temp_config_file, existing_repo_name
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Now patch out API.get_repo to return some arbitrary dict
        # Indication that everything worked okay
        mocker.patch(
            "pytoil.api.API.get_repo_names",
            autospec=True,
            return_value={"exist1", "exist2", "exist3", "exist4"},
        )

        repo = Repo(name=existing_repo_name)

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
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out urllib3.request to raise
        # other HTTP errors from our parametrize
        mocker.patch(
            "pytoil.api.API.get",
            autospec=True,
            side_effect=APIRequestError(message=message, status_code=error_code),
        )

        repo = Repo(name="myproject")

        with pytest.raises(APIRequestError):
            repo.exists_remote()


@pytest.mark.parametrize("which_return", ["", None, False])
def test_repo_clone_raises_on_invalid_git(mocker, temp_config_file, which_return):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out shutil.which
        mocker.patch(
            "pytoil.repo.shutil.which", autospec=True, return_value=which_return
        )

        with pytest.raises(GitNotInstalledError):
            repo = Repo(owner="me", name="myproject")
            repo.clone()


def test_repo_clone_raises_if_local_repo_already_exists(mocker, temp_config_file):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.shutil.which", autospec=True, return_value=True)

        # Make it think the repo already exists locally
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        with pytest.raises(LocalRepoExistsError):
            repo = Repo(owner="me", name="myproject")
            repo.clone()


def test_repo_clone_correctly_calls_git(mocker, temp_config_file):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Ensure the repo "exists" on github
        mocker.patch("pytoil.repo.Repo.exists_remote", autospec=True, return_value=True)

        # Mock the subprocess of calling git
        mock_subprocess = mocker.patch("pytoil.repo.subprocess.run", autospec=True)

        repo = Repo(name="fakerepo")

        repo.clone()

        # Assert git would have been called with correct args
        mock_subprocess.assert_called_once_with(
            ["git", "clone", "https://github.com/tempfileuser/fakerepo.git"],
            cwd=pathlib.Path("/Users/tempfileuser/projects"),
            check=True,
        )

        # Assert the path was updated
        assert repo.path == pathlib.Path("/Users/tempfileuser/projects/fakerepo")


def test_repo_clone_raises_subprocess_error_if_anything_goes_wrong(
    mocker, temp_config_file
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Ensure the repo "exists" on github
        mocker.patch("pytoil.repo.Repo.exists_remote", autospec=True, return_value=True)

        # Mock the subprocess of calling git, but have it raise an error
        mock_subprocess = mocker.patch(
            "pytoil.repo.subprocess.run",
            autospec=True,
            side_effect=[subprocess.CalledProcessError(-1, "cmd")],
        )

        repo = Repo(name="fakerepo")

        with pytest.raises(subprocess.CalledProcessError):

            repo.clone()

            # Assert git would have been called with correct args
            mock_subprocess.assert_called_once_with(
                ["git", "clone", "https://github.com/tempfileuser/fakerepo.git"],
                cwd=pathlib.Path("/Users/tempfileuser/projects"),
                check=True,
            )


def test_repo_clone_raises_on_missing_remote_repo(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Ensure the repo doesnt already exist
        mocker.patch(
            "pytoil.repo.Repo.exists_remote", autospec=True, return_value=False
        )

        repo = Repo(name="fakerepo")

        with pytest.raises(RepoNotFoundError):
            repo.clone()


def test_repo_fork_raises_on_API_error(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Best way of making an APIError is attempting to fork
        # a repo you already own
        repo = Repo(name="fakerepo", owner="tempfileuser")

        with pytest.raises(APIRequestError):
            repo.fork()


def test_repo_fork_returns_correct_url(mocker, temp_config_file):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Patch out the return from api.fork_repo
        # so it doesn't hit the API
        mocker.patch(
            "pytoil.api.API.fork_repo",
            autospec=True,
            return_value={"some": "arbitrary", "json": "blob"},
        )

        repo = Repo(name="coolproject", owner="someoneelse")

        # Should return the url of the users fork
        # ie same project name but now with new owner
        assert repo.fork() == "https://github.com/tempfileuser/coolproject.git"


@pytest.mark.parametrize(
    "file, exists",
    [
        ("here.txt", True),
        ("i_exist.yml", True),
        ("hello.py", True),
        ("me_too.json", True),
        ("not_me_though.csv", False),
        ("me_neither.toml", False),
        ("i_never_existed.cfg", False),
        ("what_file.ini", False),
    ],
)
def test_does_file_exist(
    mocker, temp_config_file, repo_folder_with_random_existing_files, file, exists
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Trick it into thinking a repo exists
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        # Test the file exists method
        assert repo._does_file_exist(file) is exists


def test_does_file_exist_raises_on_non_existent_repo(
    mocker, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Return False for repo.exists_local
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        with pytest.raises(RepoNotFoundError):
            repo._does_file_exist("here.txt")


def test_is_setuptools(
    mocker, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Return True for repo.exists_local
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        # Add in a setup.py and setup.cfg
        folder.joinpath("setup.py").touch()
        folder.joinpath("setup.cfg").touch()

        # Should now return True
        assert repo.is_setuptools() is True

        # Now remove setup.py
        folder.joinpath("setup.py").unlink()

        # Should still return True
        assert repo.is_setuptools() is True

        # Now remove setup.cfg
        folder.joinpath("setup.cfg").unlink()

        # Should now return False
        assert repo.is_setuptools() is False

        # Now just a setup.py
        folder.joinpath("setup.py").touch()

        # Should again return True
        assert repo.is_setuptools() is True


def test_is_editable(mocker, temp_config_file, repo_folder_with_random_existing_files):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Return True for repo.exists_local
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        # Add in a setup.py
        folder.joinpath("setup.py").touch()

        # Should now return True
        assert repo.is_editable() is True

        # Now remove setup.py
        folder.joinpath("setup.py").unlink()

        # Should now return False
        assert repo.is_setuptools() is False


def test_is_conda(mocker, temp_config_file, repo_folder_with_random_existing_files):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Return True for repo.exists_local
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        # Add in an environment.yml
        folder.joinpath("environment.yml").touch()

        # Should now return True
        assert repo.is_conda() is True

        # Now remove environment.yml
        folder.joinpath("environment.yml").unlink()

        # Should now return False
        assert repo.is_conda() is False


def test_is_pep517(mocker, temp_config_file, repo_folder_with_random_existing_files):

    with mocker.patch.object(pytoil.config, "CONFIG_PATH", temp_config_file):

        # Return True for repo.exists_local
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        # Add in an pyproject.toml
        folder.joinpath("pyproject.toml").touch()

        # Should now return True
        assert repo.is_pep517() is True

        # Now remove pyproject.toml
        folder.joinpath("pyproject.toml").unlink()

        # Should now return False
        assert repo.is_pep517() is False
