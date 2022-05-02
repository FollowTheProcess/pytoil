"""
Entry point for pytoil, simply passes control up
to the root click command.
"""


from __future__ import annotations

from pytoil.cli.root import main

main(_anyio_backend="asyncio")
