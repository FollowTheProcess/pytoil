from pathlib import Path

import aiofiles
import aiofiles.os
import pytest

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


@pytest.mark.asyncio
async def test_python_starter_generate():
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        starter = PythonStarter(path=Path(tmpdir), name="temptest")

        await starter.generate()

        for file in starter.files:
            assert await aiofiles.os.path.exists(file)

        async with aiofiles.open(starter.root.joinpath("README.md")) as readme:
            readme_content = await readme.read()

        async with aiofiles.open(
            starter.root.joinpath("requirements.txt")
        ) as requirements:
            requirements_content = await requirements.read()

        async with aiofiles.open(starter.root.joinpath("temptest.py")) as python:
            python_content = await python.read()

        assert readme_content == "# temptest\n"
        assert (
            requirements_content == "# Put your requirements here e.g. flask>=1.0.0\n"
        )
        assert (
            python_content
            == 'def hello(name: str = "world") -> None:\n    print(f"hello {name}")\n'
        )
