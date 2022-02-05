"""
The pytoil cache subcommand.


Author: Tom Fleet
Created: 21/01/2022
"""

from __future__ import annotations

import asyncio
import functools
import shutil

import asyncclick as click

from pytoil.api import API
from pytoil.cli.printer import printer
from pytoil.config import Config, defaults


@click.group()
async def cache() -> None:
    """
    Interact with pytoil's cache.

    Pytoil caches the responses from the GitHub API so that it
    doesn't have to hit it so often and so a user gets the snappiest
    experience possible using the CLI.

    The cache subcommand allows you to interact with this cache, either
    forcing a manual refresh or flushing it entirely.
    """


@cache.command()
@click.pass_obj
async def refresh(config: Config) -> None:
    """
    Force a manual refresh of the cache.

    This will cause pytoil to hit all the GitHub API endpoints
    it uses and cache the responses so that the next time any
    API calls are made, the responses will be served from the cache
    and not the GitHub API.

    Examples:

    $ pytoil cache refresh
    """
    api = API(username=config.username, token=config.token)
    names = await api.get_repo_names()

    # Just hit all the cacheable endpoints to initialise the cache
    await asyncio.gather(
        api.get_repos(),
        api.get_forks(),
        api.get_repo_names(),
        *[api.get_repo_info(name) for name in names],
    )

    printer.good("Cache refreshed successfully")


@cache.command()
@click.pass_obj
async def clear(config: Config) -> None:
    """
    Clear pytoil's cache.

    This will remove the entire cache forcing the next command
    using the GitHub API to fetch the latest data.

    It may be slightly slower as a result.

    Examples:

    $ pytoil cache clear
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        executor=None,
        func=functools.partial(
            shutil.rmtree,
            path=defaults.CACHE_DIR,
            ignore_errors=True,
        ),
    )

    printer.good("Cache cleared successfully")
