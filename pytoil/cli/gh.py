"""
The pytoil gh command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
import httpx
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.repo import Repo


@click.command()
@click.argument("project", nargs=1)
async def gh(project: str) -> None:
    """
    Open one of your projects on GitHub.

    Given a project name (must exist on GitHub and be owned by you),
    'gh' will open your browser and navigate to the project on GitHub.

    Examples:

    $ pytoil gh my_project
    """
    config = await Config.from_file()
    if not config.can_use_api():
        msg.warn(
            "You must set your GitHub username and personal access token to use API"
            " features.",
            exits=1,
        )

    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )

    try:
        exists = await repo.exists_remote(api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_error(err)
    else:
        if not exists:
            msg.warn(f"Could not find {project!r} on GitHub. Was it a typo?", exits=1)
        else:
            msg.info(f"Opening {project!r} on GitHub")
            click.launch(url=repo.html_url)
