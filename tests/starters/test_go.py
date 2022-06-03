from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import GoNotInstalledError
from pytoil.starters import GoStarter


def test_go_starter_init():
    starter = GoStarter(path=Path("somewhere"), name="testygo", go="notgo")

    assert starter.path == Path("somewhere")
    assert starter.name == "testygo"
    assert starter.root == Path("somewhere").joinpath("testygo").resolve()
    assert starter.files == [
        Path("somewhere").joinpath("testygo").resolve().joinpath("README.md"),
        Path("somewhere").joinpath("testygo").resolve().joinpath("main.go"),
    ]


def test_generate_raises_if_go_not_installed():
    starter = GoStarter(path=Path("somewhere"), name="testygo", go=None)

    with pytest.raises(GoNotInstalledError):
        starter.generate()


def test_go_starter_generate(mocker: MockerFixture):
    with tempfile.TemporaryDirectory() as tmpdir:
        starter = GoStarter(path=Path(tmpdir), name="tempgo", go="notgo")

        mock_go_mod_init = mocker.patch(
            "pytoil.starters.go.subprocess.run", autospec=True
        )

        starter.generate(username="me")

        mock_go_mod_init.assert_called_once_with(
            ["notgo", "mod", "init", "github.com/me/tempgo"],
            cwd=starter.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        for file in starter.files:
            assert file.exists()

        with open(starter.root.joinpath("README.md")) as readme:
            readme_content = readme.read()

        with open(starter.root.joinpath("main.go")) as main_go:
            main_go_content = main_go.read()

        assert readme_content == "# tempgo\n"
        assert (
            main_go_content
            == 'package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello'
            ' World")\n}\n'
        )
