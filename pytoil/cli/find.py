"""
The pytoil find command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncclick as click
from rich.console import Console
from rich.table import Table, box
from rich.text import Text
from thefuzz import process

from pytoil.api import API
from pytoil.cli.printer import printer
from pytoil.config import Config

FUZZY_SCORE_CUTOFF = 75


@click.command()
@click.argument("project", nargs=1)
@click.option(
    "-l",
    "--limit",
    type=int,
    default=5,
    help="Limit results to maximum number.",
    show_default=True,
)
@click.pass_obj
async def find(config: Config, project: str, limit: int) -> None:
    """
    Quickly locate a project.

    The find command provides a fuzzy search for finding a project when you
    don't know where it is (local or on GitHub).

    It will perform a fuzzy search through all your local and remote projects,
    bring back the best matches and show you where they are.

    Useful if you have a lot of projects and you can't quite remember
    what the one you want is called!

    The "-l/--limit" flag can be used to alter the number of returned
    search results, but bare in mind that matches with sufficient match score
    are returned anyway so the results flag only limits the maximum number
    of results shown.

    Examples:

    $ pytoil find my

    $ pytoil find proj --limit 3
    """
    api = API(username=config.username, token=config.token)

    local_projects: set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }
    remote_projects = await api.get_repo_names()

    all_projects = local_projects.union(remote_projects)

    matches: list[tuple[str, int]] = process.extractBests(
        project, all_projects, limit=limit, score_cutoff=FUZZY_SCORE_CUTOFF
    )

    table = Table(box=box.SIMPLE)
    table.add_column("Project", style="bold white")
    table.add_column("Similarity")
    table.add_column("Where")

    if len(matches) == 0:
        printer.error("No matches found!", exits=1)

    for match in matches:
        is_local = match[0] in local_projects
        table.add_row(
            match[0],
            str(match[1]),
            Text("Local", style="green")
            if is_local
            else Text("Remote", style="dark_orange"),
        )

    console = Console()
    console.print(table)
