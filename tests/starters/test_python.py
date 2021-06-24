"""
Tests for the python starter template generation.

Author: Tom Fleet
Created: 24/06/2021
"""

import shutil
from pathlib import Path

from pytoil.starters import PythonStarter

TESTDATA = Path(__file__).parent.parent.joinpath("testdata").resolve()


def test_python_starter_init():

    starter = PythonStarter(path=Path("somewhere/else"), name="testpython")

    assert starter.path == Path("somewhere/else")
    assert starter.name == "testpython"
    assert starter.root == Path("somewhere/else").joinpath("testpython")
    assert starter.files == [
        starter.root.joinpath(filename) for filename in starter._files
    ]


def test_python_starter_repr():

    starter = PythonStarter(path=Path("somewhere/else"), name="testpython")

    assert (
        repr(starter) == f"PythonStarter(path={starter.path!r}, name={starter.name!r})"
    )


class TestPythonGenerate:

    path = TESTDATA

    def setup_method(self):
        self.starter = PythonStarter(path=self.path, name="py_starter")
        # Make the starter
        self.starter.generate()

    def test_generate_created_correct_files(self):

        for file in self.starter.files:
            assert file.exists()

    def test_readme_has_correct_text(self):
        readme = self.starter.root.joinpath("README.md")
        readme_text = readme.read_text(encoding="utf-8")

        assert readme_text == f"# {self.starter.name}\n"

    def test_python_file_has_correct_text(self):
        py_file = self.starter.root.joinpath(f"{self.starter.name}.py")
        py_text = py_file.read_text(encoding="utf-8")

        assert (
            py_text
            == 'def hello(name: str = "world") -> None:\n\tprint(f"hello {name}")\n'
        )

    def test_requirements_txt_has_correct_text(self):
        req_file = self.starter.root.joinpath("requirements.txt")
        req_text = req_file.read_text(encoding="utf-8")

        assert req_text == "# Put your requirements here e.g. flask>=1.0.0\n"

    def teardown_method(self):
        # Clean the created stuff
        shutil.rmtree(self.starter.root)

        # Error if the files have not been cleaned up for
        # whatever reason
        for file in self.starter.files:
            assert not file.exists()
