"""
Entry point for pytoil, simply passes control up
to the root click command.
"""


from pytoil.cli.root import main

main(_anyio_backend="asyncio")
