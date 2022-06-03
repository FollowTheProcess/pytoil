from __future__ import annotations

from click.testing import CliRunner

from pytoil.cli.root import main


def test_cli_doesnt_blow_up():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])

    assert result.exit_code == 0
    assert "Helpful CLI to automate the development workflow" in result.stdout
