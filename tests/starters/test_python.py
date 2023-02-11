from __future__ import annotations

import tempfile
from pathlib import Path

from pytoil.starters import PythonStarter


def test_python_starter_init() -> None:
    starter = PythonStarter(path=Path("somewhere"), name="testypython")

    assert starter.path == Path("somewhere")
    assert starter.name == "testypython"
    assert starter.root == Path("somewhere").joinpath("testypython").resolve()
    assert starter.files == [
        Path("somewhere").joinpath("testypython").resolve().joinpath("README.md"),
        Path("somewhere")
        .joinpath("testypython")
        .resolve()
        .joinpath("requirements.txt"),
        Path("somewhere").joinpath("testypython").resolve().joinpath("testypython.py"),
    ]


def test_python_starter_generate() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        starter = PythonStarter(path=Path(tmpdir), name="temptest")

        starter.generate()

        for file in starter.files:
            assert file.exists()

        readme_content = starter.root.joinpath("README.md").read_text()
        requirements_content = starter.root.joinpath("requirements.txt").read_text()
        python_content = starter.root.joinpath("temptest.py").read_text()

        assert readme_content == "# temptest\n"
        assert (
            requirements_content == "# Put your requirements here e.g. flask>=1.0.0\n"
        )
        assert (
            python_content
            == 'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )
