from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from pytest_mock import MockerFixture
from pytoil.exceptions import CargoNotInstalledError
from pytoil.starters import RustStarter


def test_go_starter_init() -> None:
    starter = RustStarter(path=Path("somewhere"), name="testyrust", cargo="notcargo")

    assert starter.path == Path("somewhere")
    assert starter.name == "testyrust"
    assert starter.root == Path("somewhere").joinpath("testyrust").resolve()
    assert starter.files == [
        Path("somewhere").joinpath("testyrust").resolve().joinpath("README.md"),
    ]


def test_generate_raises_if_cargo_not_installed() -> None:
    starter = RustStarter(path=Path("somewhere"), name="testyrust", cargo=None)

    with pytest.raises(CargoNotInstalledError):
        starter.generate()


def test_rust_starter_generate(mocker: MockerFixture) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        starter = RustStarter(path=Path(tmpdir), name="temprust", cargo="notcargo")

        mock_cargo_init = mocker.patch(
            "pytoil.starters.rust.subprocess.run", autospec=True
        )

        starter.generate()

        mock_cargo_init.assert_called_once_with(
            ["notcargo", "init", "--vcs", "none"],
            cwd=starter.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        for file in starter.files:
            assert file.exists()

        readme_content = starter.root.joinpath("README.md").read_text()

        assert readme_content == "# temprust\n"
