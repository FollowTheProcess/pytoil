import sys
from pathlib import Path

import aiofiles
import aiofiles.os
import pytest
from pytest_mock import MockerFixture

from pytoil.exceptions import CargoNotInstalledError
from pytoil.starters import RustStarter


def test_go_starter_init():
    starter = RustStarter(path=Path("somewhere"), name="testyrust", cargo="notcargo")

    assert starter.path == Path("somewhere")
    assert starter.name == "testyrust"
    assert starter.root == Path("somewhere").joinpath("testyrust").resolve()
    assert starter.files == [
        Path("somewhere").joinpath("testyrust").resolve().joinpath("README.md"),
    ]


@pytest.mark.asyncio
async def test_generate_raises_if_cargo_not_installed():
    starter = RustStarter(path=Path("somewhere"), name="testyrust", cargo=None)

    with pytest.raises(CargoNotInstalledError):
        await starter.generate()


@pytest.mark.asyncio
async def test_rust_starter_generate(mocker: MockerFixture):
    async with aiofiles.tempfile.TemporaryDirectory() as tmpdir:
        starter = RustStarter(path=Path(tmpdir), name="temprust", cargo="notcargo")

        mock_cargo_init = mocker.patch(
            "pytoil.starters.rust.asyncio.create_subprocess_exec", autospec=True
        )

        await starter.generate()

        mock_cargo_init.assert_called_once_with(
            "notcargo",
            "init",
            "--vcs",
            "none",
            cwd=starter.root,
            stdout=sys.stdout,
            stderr=sys.stderr,
        )

        for file in starter.files:
            assert await aiofiles.os.path.exists(file)

        async with aiofiles.open(starter.root.joinpath("README.md")) as readme:
            readme_content = await readme.read()

        assert readme_content == "# temprust\n"
