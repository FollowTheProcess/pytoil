"""
The pytoil info command.


Author: Tom Fleet
Created: 21/12/2021
"""

import asyncclick as click
from rich.console import Console
from rich.table import Table, box
from wasabi import msg

from pytoil.api import API
from pytoil.config import Config
from pytoil.exceptions import RepoNotFoundError
from pytoil.repo import Repo


@click.command()
@click.argument("project", nargs=1)
async def info(project: str) -> None:
    """
    Get useful info for a project.

    Given a project name (can be local or remote), 'info' will return a summary
    description of the project.

    If the project is on GitHub, info will prefer getting information from the GitHub
    API as this is more detailed.

    If the project is local only, some information is extracted from the operating
    system about the project.

    Examples:

    $ pytoil info my_project
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
        info = await repo.info(api)
    except RepoNotFoundError:
        msg.warn(f"{project!r} not found locally or on GitHub. Was it a typo?", exits=1)
    else:
        click.secho(f"\nInfo for {project!r}:\n", fg="cyan", bold=True)

        table = Table(box=box.SIMPLE)
        table.add_column("Key", style="cyan", justify="right")
        table.add_column("Value", justify="left")

        for key, val in info.items():
            table.add_row(f"{key}:", str(val))

        console = Console()
        console.print(table)
