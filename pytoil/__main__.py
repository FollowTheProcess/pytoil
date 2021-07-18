"""
Entry point for pytoil, simply passes control up to
the root Typer `app`.
"""

from pytoil.cli.root import app

app(prog_name="pytoil")
