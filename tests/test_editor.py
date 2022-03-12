import sys
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from pytoil.editor import launch


@pytest.mark.asyncio
async def test_launch(mocker: MockerFixture):
    mock = mocker.patch(
        "pytoil.editor.editor.asyncio.create_subprocess_exec", autospec=True
    )

    await launch(path=Path("somewhere"), bin="/path/to/editor")

    mock.assert_called_once_with(
        "/path/to/editor", Path("somewhere"), stdout=sys.stdout, stderr=sys.stderr
    )
