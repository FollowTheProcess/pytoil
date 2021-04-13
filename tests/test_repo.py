"""
Tests for the repo module.

Author: Tom Fleet
Created: 05/02/2021
"""


import pathlib
import subprocess
from typing import NamedTuple

import pytest
from pytest_mock import MockerFixture

import pytoil
from pytoil.environments import CondaEnv, VirtualEnv
from pytoil.exceptions import (
    GitNotInstalledError,
    InvalidRepoPathError,
    InvalidURLError,
    LocalRepoExistsError,
    RepoNotFoundError,
)
from pytoil.repo import Repo


def test_repo_init(mocker: MockerFixture, temp_config_file):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        repo = Repo(owner="me", name="myproject")

        assert repo.owner == "me"
        assert repo.name == "myproject"
        assert repo.url == "https://github.com/me/myproject.git"
        assert repo.path == pathlib.Path("/Users/tempfileuser/projects/myproject")


def test_repo_init_defaults(mocker: MockerFixture, temp_config_file):

    # Patch out the config path to be our temp file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # name is required
        repo = Repo(name="diffproject")

        assert repo.owner == "tempfileuser"
        assert repo.name == "diffproject"
        assert repo.url == "https://github.com/tempfileuser/diffproject.git"
        assert repo.path == pathlib.Path("/Users/tempfileuser/projects/diffproject")


def test_repo_repr(mocker: MockerFixture, temp_config_file):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        repo = Repo(owner="me", name="myproject")

        assert repo.__repr__() == "Repo(owner='me', name='myproject')"


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
def test_repo_from_url(mocker: MockerFixture, temp_config_file, url, owner, name):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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
def test_repo_from_url_raises_on_bad_url(mocker: MockerFixture, temp_config_file, url):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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
def test_repo_from_path(
    mocker: MockerFixture, temp_config_file, path, owner, name, url
):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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
def test_repo_from_path_raises_on_bad_path(
    mocker: MockerFixture, temp_config_file, path
):

    # Patch out to our fake config file to make sure it grabs from the config
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        with pytest.raises(InvalidRepoPathError):
            Repo.from_path(path=path)


def test_repo_exists_local_returns_true_if_path_exists(
    mocker: MockerFixture, temp_config_file
):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Patch out Repo.path to something we know exists: this file
        with mocker.patch.object(pytoil.repo.Repo, "path", pathlib.Path(__file__)):

            repo = Repo(name="fakerepo")

            assert repo.exists_local() is True


def test_repo_exists_local_returns_false_if_path_doesnt_exist(
    mocker: MockerFixture, temp_config_file
):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Patch out Repo.path to something we know doesn't exist
        with mocker.patch.object(pytoil.repo.Repo, "path", pathlib.Path("not/here")):

            repo = Repo(name="fakerepo")

            assert repo.exists_local() is False


@pytest.mark.parametrize(
    "non_existing_repo_name", ["noexist1", "noexist2", "noexist3", "noexist4"]
)
def test_repo_exists_remote_returns_false_on_missing_repo(
    mocker: MockerFixture, temp_config_file, non_existing_repo_name
):

    # Patch out the config file to point to our temporary one
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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
    mocker: MockerFixture, temp_config_file, existing_repo_name
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Now patch out API.get_repo to return some arbitrary dict
        # Indication that everything worked okay
        mocker.patch(
            "pytoil.api.API.get_repo_names",
            autospec=True,
            return_value={"exist1", "exist2", "exist3", "exist4"},
        )

        repo = Repo(name=existing_repo_name)

        assert repo.exists_remote() is True


@pytest.mark.parametrize("which_return", ["", None, False])
def test_repo_clone_raises_on_invalid_git(
    mocker: MockerFixture, temp_config_file, which_return
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Patch out shutil.which
        mocker.patch(
            "pytoil.repo.repo.shutil.which", autospec=True, return_value=which_return
        )

        with pytest.raises(GitNotInstalledError):
            repo = Repo(owner="me", name="myproject")
            repo.clone()


@pytest.mark.parametrize("which_return", ["", None, False])
def test_repo_init_raises_on_invalid_git(
    mocker: MockerFixture, temp_config_file, which_return
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Patch out shutil.which
        mocker.patch(
            "pytoil.repo.repo.shutil.which", autospec=True, return_value=which_return
        )

        with pytest.raises(GitNotInstalledError):
            repo = Repo(owner="me", name="myproject")
            repo.init()


def test_repo_clone_raises_if_local_repo_already_exists(
    mocker: MockerFixture, temp_config_file
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.repo.shutil.which", autospec=True, return_value=True)

        # Make it think the repo already exists locally
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        with pytest.raises(LocalRepoExistsError):
            repo = Repo(owner="me", name="myproject")
            repo.clone()


def test_repo_clone_correctly_calls_git(mocker: MockerFixture, temp_config_file):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Ensure the repo "exists" on github
        mocker.patch("pytoil.repo.Repo.exists_remote", autospec=True, return_value=True)

        # Mock the subprocess of calling git
        mock_subprocess = mocker.patch("pytoil.repo.repo.subprocess.run", autospec=True)

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


def test_repo_init_correctly_calls_git(mocker: MockerFixture, temp_config_file):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Mock the subprocess of calling git
        mock_subprocess = mocker.patch("pytoil.repo.repo.subprocess.run", autospec=True)

        repo = Repo(name="fakerepo")

        repo.init()

        # Assert git would have been called with correct args
        mock_subprocess.assert_called_once_with(
            ["git", "init"],
            cwd=pathlib.Path("/Users/tempfileuser/projects/fakerepo"),
            check=True,
        )


def test_repo_clone_raises_subprocess_error_if_anything_goes_wrong(
    mocker: MockerFixture, temp_config_file
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Ensure the repo "exists" on github
        mocker.patch("pytoil.repo.Repo.exists_remote", autospec=True, return_value=True)

        # Mock the subprocess of calling git, but have it raise an error
        mock_subprocess = mocker.patch(
            "pytoil.repo.repo.subprocess.run",
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


def test_repo_init_raises_subprocess_error_if_anything_goes_wrong(
    mocker: MockerFixture, temp_config_file
):

    # Same trick with the config file
    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Mock the subprocess of calling git, but have it raise an error
        mock_subprocess = mocker.patch(
            "pytoil.repo.repo.subprocess.run",
            autospec=True,
            side_effect=[subprocess.CalledProcessError(-1, "cmd")],
        )

        repo = Repo(name="fakerepo")

        with pytest.raises(subprocess.CalledProcessError):

            repo.init()

            # Assert git would have been called with correct args
            mock_subprocess.assert_called_once_with(
                ["git", "clone"],
                cwd=pathlib.Path("/Users/tempfileuser/projects/fakerepo"),
                check=True,
            )


def test_repo_clone_raises_on_missing_remote_repo(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Make it look like we have a valid git
        mocker.patch("pytoil.repo.repo.shutil.which", autospec=True, return_value=True)

        # Ensure the repo doesnt already exist
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        # Ensure the repo doesnt already exist
        mocker.patch(
            "pytoil.repo.Repo.exists_remote", autospec=True, return_value=False
        )

        repo = Repo(name="fakerepo")

        with pytest.raises(RepoNotFoundError):
            repo.clone()


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
    mocker: MockerFixture,
    temp_config_file,
    repo_folder_with_random_existing_files,
    file,
    exists,
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Trick it into thinking a repo exists
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=True)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        # Test the file exists method
        assert repo._does_file_exist(file) is exists


def test_does_file_exist_raises_on_non_existent_repo(
    mocker: MockerFixture, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Return False for repo.exists_local
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        folder: pathlib.Path = repo_folder_with_random_existing_files

        repo = Repo(name="myrepo")

        # Set the repo path to point to our folder
        repo.path = folder

        with pytest.raises(RepoNotFoundError):
            repo._does_file_exist("here.txt")


def test_is_setuptools(
    mocker: MockerFixture, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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


def test_is_editable(
    mocker: MockerFixture, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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


def test_is_conda(
    mocker: MockerFixture, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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


def test_is_pep517(
    mocker: MockerFixture, temp_config_file, repo_folder_with_random_existing_files
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

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


@pytest.mark.parametrize(
    "repo_name, description, created_at, updated_at, size, license_name, exist_local,"
    + " exist_remote",
    [
        (
            "repo1",
            "my project",
            "2020-02-27",
            "2020-04-02",
            4096,
            "MIT License",
            True,
            True,
        ),
        (
            "repo2",
            "someguys project",
            "2021-01-18",
            "2021-01-23",
            1024,
            "Apache 2.0",
            False,
            True,
        ),
        (
            "repo3",
            "somegirls project",
            "2020-07-01",
            "2021-02-28",
            2048,
            "GPL v3",
            True,
            True,
        ),
    ],
)
def test_info_on_remote_repo(
    mocker: MockerFixture,
    temp_config_file,
    repo_name,
    description,
    created_at,
    updated_at,
    size,
    license_name,
    exist_remote,
    exist_local,
):
    """
    If a repo exists remotely, regardless of whether or not it is also
    local. info should return info from the API as it is more detailed.
    """

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Convince it the repo exists remotely and locally
        mocker.patch(
            "pytoil.repo.Repo.exists_remote", autospec=True, return_value=exist_remote
        )
        mocker.patch(
            "pytoil.repo.Repo.exists_local", autospec=True, return_value=exist_local
        )

        # Have the get_repo_info method just return our made up dict
        mocker.patch(
            "pytoil.api.API.get_repo_info",
            autospec=True,
            return_value={
                "name": repo_name,
                "description": description,
                "created_at": created_at,
                "updated_at": updated_at,
                "size": size,
                "license": license_name,
                "local": exist_local,
                "remote": exist_remote,
            },
        )

        repo = Repo(name=repo_name)

        assert repo.info() == {
            "name": repo_name,
            "description": description,
            "created_at": created_at,
            "updated_at": updated_at,
            "size": size,
            "license": license_name,
            "local": exist_local,
            "remote": exist_remote,
        }


@pytest.mark.parametrize(
    "repo_name, created_at, updated_at, size, exist_local, exist_remote",
    [
        (
            "repo1",
            "2021-03-01 10:43:19",
            "2021-03-01 10:48:19",
            4096,
            True,
            False,
        ),
        (
            "repo2",
            "2021-03-01 10:43:19",
            "2021-03-01 10:48:19",
            1024,
            True,
            False,
        ),
        (
            "repo3",
            "2021-03-01 10:43:19",
            "2021-03-01 10:48:19",
            2048,
            True,
            False,
        ),
    ],
)
def test_info_on_local_only_repo(
    mocker: MockerFixture,
    temp_config_file,
    repo_name,
    created_at,
    updated_at,
    size,
    exist_remote,
    exist_local,
):
    """
    If a repo exists locally only, we should instead get some info from Path.stat.

    This one is quite complicated because you can't mock out datetime
    so instead we:
    - patch out everything related to whether or not the repo exists
    - Create a fake dataclass `FakeStat`
    - This FakeStat houses the unix timestamps that datetime.strftime can operate on
    - In the parametrize we have the strftime outputs for those timestamps
    """

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Convince it the repo exists remotely and locally
        mocker.patch(
            "pytoil.repo.Repo.exists_remote", autospec=True, return_value=exist_remote
        )
        mocker.patch(
            "pytoil.repo.Repo.exists_local", autospec=True, return_value=exist_local
        )

        # Have the get_repo_info method just return our made up dict
        mocker.patch(
            "pytoil.api.API.get_repo_info",
            autospec=True,
            return_value={
                "name": repo_name,
                "created_at": created_at,
                "updated_at": updated_at,
                "size": size,
                "local": exist_local,
                "remote": exist_remote,
            },
        )

        class FakeStat(NamedTuple):
            st_ctime = 1614595399
            st_mtime = 1614595699
            st_size = size

        mocker.patch(
            "pytoil.repo.repo.pathlib.Path.stat", autospec=True, return_value=FakeStat()
        )

        repo = Repo(name=repo_name)

        assert repo.info() == {
            "name": repo_name,
            "created_at": created_at,
            "updated_at": updated_at,
            "size": size,
            "local": exist_local,
            "remote": exist_remote,
        }


def test_repo_info_raises_if_doesnt_exist_locally_or_remotely(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        # Convince it the repo does not exist remotely or locally
        mocker.patch(
            "pytoil.repo.Repo.exists_remote", autospec=True, return_value=False
        )
        mocker.patch("pytoil.repo.Repo.exists_local", autospec=True, return_value=False)

        with pytest.raises(RepoNotFoundError):
            repo = Repo(name="blah")
            repo.info()


def test_repo_dispatch_env_correctly_identifies_conda(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=True)

        repo = Repo(name="test")

        env = repo.dispatch_env()

        assert isinstance(env, CondaEnv)


def test_repo_dispatch_env_correctly_identifies_virtualenv(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=False)

        mocker.patch("pytoil.repo.Repo.is_setuptools", autospec=True, return_value=True)

        repo = Repo(name="test")

        env = repo.dispatch_env()

        assert isinstance(env, VirtualEnv)


def test_repo_dispatch_env_returns_none_when_it_cant_detect(
    mocker: MockerFixture, temp_config_file
):

    with mocker.patch.object(pytoil.config.config, "CONFIG_PATH", temp_config_file):

        mocker.patch("pytoil.repo.Repo.is_conda", autospec=True, return_value=False)

        mocker.patch(
            "pytoil.repo.Repo.is_setuptools", autospec=True, return_value=False
        )

        repo = Repo(name="test")

        env = repo.dispatch_env()

        assert env is None
