"""
Tests for the repo module.

Author: Tom Fleet
Created: 05/02/2021
"""

import pathlib

from pytoil.repo import Repo


def test_repo_init():

    repo = Repo(owner="me", name="myproject")

    assert repo.owner == "me"
    assert repo.name == "myproject"
    assert repo.url == "https://github.com/me/myproject.git"
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
