"""
Tests for the rust starter template generation.

Author: Tom Fleet
Created: 24/06/2021
"""

from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import CargoNotInstalledError
from pytoil.starters import RustStarter


def test_rust_starter_init():

    starter = RustStarter(path=Path("somewhere/else"), name="testrust")

    assert starter.path == Path("somewhere/else")
    assert starter.name == "testrust"
    assert starter.root == Path("somewhere/else").joinpath("testrust")
    assert starter.files == [
        starter.root.joinpath(filename) for filename in starter._files
    ]


def test_rust_starter_repr():

    starter = RustStarter(path=Path("somewhere/else"), name="testrust")

    assert repr(starter) == f"RustStarter(path={starter.path!r}, name={starter.name!r})"


def test_generate_creates_correct_files(fake_projects_dir, mocker: MockerFixture):

    starter = RustStarter(path=fake_projects_dir, name="rust_starter")

    # Make sure it doesn't actually call cargo
    mocker.patch("pytoil.starters.rust.subprocess.run", autospec=True)

    # Make sure it doesn't raise if cargo isn't on $PATH
    mocker.patch(
        "pytoil.starters.rust.shutil.which", autospec=True, return_value="cargo"
    )

    starter.generate()

    for file in starter.files:
        assert file.exists()


def test_generated_readme_has_correct_text(fake_projects_dir, mocker: MockerFixture):

    starter = RustStarter(path=fake_projects_dir, name="rust_starter")

    # Make sure it doesn't actually call cargo
    mocker.patch("pytoil.starters.rust.subprocess.run", autospec=True)

    # Make sure it doesn't raise if cargo isn't on $PATH
    mocker.patch(
        "pytoil.starters.rust.shutil.which", autospec=True, return_value="cargo"
    )

    starter.generate()

    readme = starter.root.joinpath("README.md")
    readme_text = readme.read_text(encoding="utf-8")

    assert readme_text == f"# {starter.name}\n"


def test_cargo_init_called_properly(fake_projects_dir, mocker: MockerFixture):

    starter = RustStarter(path=fake_projects_dir, name="rust_starter")

    # Make sure it doesn't actually call cargo
    mock_mod_init = mocker.patch("pytoil.starters.rust.subprocess.run", autospec=True)

    # Make sure it doesn't raise if cargo isn't on $PATH
    mocker.patch(
        "pytoil.starters.rust.shutil.which", autospec=True, return_value="cargo"
    )

    starter.generate()

    mock_mod_init.assert_called_once_with(
        ["cargo", "init"],
        check=True,
        capture_output=True,
        cwd=starter.root,
    )


@pytest.mark.parametrize("shutil_return", ["", None, False])
def test_raise_for_cargo_raises_if_cargo_not_installed(
    mocker: MockerFixture, shutil_return, fake_projects_dir
):

    starter = RustStarter(path=fake_projects_dir, name="rust_starter")

    mocker.patch(
        "pytoil.starters.rust.shutil.which", autospec=True, return_value=shutil_return
    )

    with pytest.raises(CargoNotInstalledError):
        starter.raise_for_cargo()
