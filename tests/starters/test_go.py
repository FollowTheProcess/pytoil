"""
Tests for the go starter template generation.

Author: Tom Fleet
Created: 24/06/2021
"""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.config import Config
from pytoil.exceptions import GoNotInstalledError
from pytoil.starters import GoStarter

TESTDATA = Path(__file__).parent.parent.joinpath("testdata").resolve()
FAKE_CONFIG = TESTDATA / ".pytoil.yml"


def test_go_starter_init():

    starter = GoStarter(path=Path("somewhere/else"), name="testgo")

    assert starter.path == Path("somewhere/else")
    assert starter.name == "testgo"
    assert starter.root == Path("somewhere/else").joinpath("testgo")
    assert starter.files == [
        starter.root.joinpath(filename) for filename in starter._files
    ]


def test_go_starter_repr():

    starter = GoStarter(path=Path("somewhere/else"), name="testgo")

    assert repr(starter) == f"GoStarter(path={starter.path!r}, name={starter.name!r})"


def test_generate_creates_correct_files(fake_projects_dir, mocker: MockerFixture):

    starter = GoStarter(path=fake_projects_dir, name="go_starter")

    # Make sure it doesn't actually call go
    mocker.patch("pytoil.starters.go.subprocess.run", autospec=True)

    # Make sure it doesn't raise if go isn't on $PATH
    mocker.patch("pytoil.starters.go.shutil.which", autospec=True, return_value="go")

    config = Config.from_file(FAKE_CONFIG)

    starter.generate(username=config.username)

    for file in starter.files:
        assert file.exists()


def test_generated_readme_has_correct_text(fake_projects_dir, mocker: MockerFixture):

    starter = GoStarter(path=fake_projects_dir, name="go_starter")

    # Make sure it doesn't actually call go
    mocker.patch("pytoil.starters.go.subprocess.run", autospec=True)

    # Make sure it doesn't raise if go isn't on $PATH
    mocker.patch("pytoil.starters.go.shutil.which", autospec=True, return_value="go")

    config = Config.from_file(FAKE_CONFIG)

    starter.generate(username=config.username)

    readme = starter.root.joinpath("README.md")
    readme_text = readme.read_text(encoding="utf-8")

    assert readme_text == f"# {starter.name}\n"


def test_generated_go_file_has_correct_text(fake_projects_dir, mocker: MockerFixture):

    starter = GoStarter(path=fake_projects_dir, name="go_starter")

    # Make sure it doesn't actually call go
    mocker.patch("pytoil.starters.go.subprocess.run", autospec=True)

    # Make sure it doesn't raise if go isn't on $PATH
    mocker.patch("pytoil.starters.go.shutil.which", autospec=True, return_value="go")

    config = Config.from_file(FAKE_CONFIG)

    starter.generate(username=config.username)

    go_file = starter.root.joinpath("main.go")
    go_text = go_file.read_text(encoding="utf-8")

    assert (
        go_text
        == 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello World")\n}\n'  # noqa: E501
    )


def test_go_mod_init_called_properly(fake_projects_dir, mocker: MockerFixture):

    starter = GoStarter(path=fake_projects_dir, name="go_starter")

    # Make sure it doesn't actually call go
    mock_mod_init = mocker.patch("pytoil.starters.go.subprocess.run", autospec=True)

    # Make sure it doesn't raise if go isn't on $PATH
    mocker.patch("pytoil.starters.go.shutil.which", autospec=True, return_value="go")

    config = Config.from_file(FAKE_CONFIG)

    starter.generate(username=config.username)

    mock_mod_init.assert_called_once_with(
        ["go", "mod", "init", f"github.com/{config.username}/{starter.name}"],
        check=True,
        capture_output=True,
        cwd=starter.root,
    )


@pytest.mark.parametrize("shutil_return", ["", None, False])
def test_raise_for_go_raises_if_go_not_installed(
    mocker: MockerFixture, shutil_return, fake_projects_dir
):

    starter = GoStarter(path=fake_projects_dir, name="go_starter")

    mocker.patch(
        "pytoil.starters.go.shutil.which", autospec=True, return_value=shutil_return
    )

    with pytest.raises(GoNotInstalledError):
        starter.raise_for_go()
