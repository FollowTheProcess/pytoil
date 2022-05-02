"""
The pytoil gh command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
import httpx

from pytoil.api import API
from pytoil.cli import utils
from pytoil.cli.printer import printer
from pytoil.config import Config
from pytoil.repo import Repo


@click.command()
@click.argument("project", nargs=1)
@click.option("-i", "--issues", is_flag=True, help="Go to the issues page.")
@click.option("-p", "--prs", is_flag=True, help="Go to the pull requests page.")
@click.pass_obj
async def gh(config: Config, project: str, issues: bool, prs: bool) -> None:
    """
    Open one of your projects on GitHub.

    Given a project name (must exist on GitHub and be owned by you),
    'gh' will open your browser and navigate to the project on GitHub.

    You can also use the "--issues" or "--prs" flags to immediately
    open up the repo's issues or pull requests page.

    Examples:

    $ pytoil gh my_project

    $ pytoil gh my_project --issues

    $ pytoil gh my_project --prs
    """
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
            printer.error(
                f"Could not find {project!r} on GitHub. Was it a typo?", exits=1
            )
        if issues:
            printer.info(f"Opening {project}'s issues on GitHub")
            click.launch(url=repo.issues_url)
        elif prs:
            printer.info(f"Opening {project}'s pull requests on GitHub")
            click.launch(url=repo.pulls_url)
        else:
            printer.info(f"Opening {project} on GitHub")
            click.launch(url=repo.html_url)
