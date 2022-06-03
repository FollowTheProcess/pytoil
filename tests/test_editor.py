from __future__ import annotations

import sys
from pathlib import Path

from pytest_mock import MockerFixture

from pytoil.editor import launch


def test_launch(mocker: MockerFixture):
    mock = mocker.patch("pytoil.editor.editor.subprocess.run", autospec=True)

    launch(path=Path("somewhere"), bin="/path/to/editor")

    mock.assert_called_once_with(
        ["/path/to/editor", Path("somewhere")], stdout=sys.stdout, stderr=sys.stderr
    )
