from __future__ import annotations

import tempfile
from pathlib import Path

from pytoil.starters import PythonStarter


def test_python_starter_init():
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


def test_python_starter_generate():
    with tempfile.TemporaryDirectory() as tmpdir:
        starter = PythonStarter(path=Path(tmpdir), name="temptest")

        starter.generate()

        for file in starter.files:
            assert file.exists()

        with open(starter.root.joinpath("README.md")) as readme:
            readme_content = readme.read()

        with open(starter.root.joinpath("requirements.txt")) as requirements:
            requirements_content = requirements.read()

        with open(starter.root.joinpath("temptest.py")) as python:
            python_content = python.read()

        assert readme_content == "# temptest\n"
        assert (
            requirements_content == "# Put your requirements here e.g. flask>=1.0.0\n"
        )
        assert (
            python_content
            == 'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )
