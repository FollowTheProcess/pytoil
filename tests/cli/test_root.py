from __future__ import annotations

import pytest
from asyncclick.testing import CliRunner

from pytoil.cli.root import main


@pytest.mark.asyncio
async def test_cli_doesnt_blow_up():
    runner = CliRunner()
    result = await runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Helpful CLI to automate the development workflow" in result.stdout
