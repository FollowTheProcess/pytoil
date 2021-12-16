"""
The pytoil find command.


Author: Tom Fleet
Created: 16/12/2021
"""

from typing import List, Tuple

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from thefuzz import process
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config

app = typer.Typer()

FUZZY_SCORE_CUTOFF = 75


@app.command()
def find(
    project: str = typer.Argument(
        None, help="Name of the project to find.", show_default=False
    ),
    results: int = typer.Option(
        3, "--results", "-r", help="Limit results to maximum number."
    ),
) -> None:
    """
    Quickly locate a project.

    The find command provides a fuzzy search for finding a project when you
    don't know where it is (local or on GitHub).

    It will perform a fuzzy search through all your local and remote projects,
    bring back the best matches and show you where they are.

    Useful if you have a lot of projects and you can't quite remember
    what the one you want is called!

    The "-r/--results" flag can be used to alter the number of returned
    search results, but bare in mind that matches with sufficient match score
    are returned anyway so the results flag only limits the maximum number
    of results shown.

    Examples:

    $ pytoil find my

    $ pytoil find proj --results 5
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    local_projects = utils.get_local_projects(path=config.projects_dir)
    remote_projects = api.get_repo_names()

    all_projects = local_projects.union(remote_projects)

    matches: List[Tuple[str, int]] = process.extractBests(
        project, all_projects, limit=results, score_cutoff=FUZZY_SCORE_CUTOFF
    )

    table = Table(box=box.SIMPLE)
    table.add_column("Project", style="cyan", justify="center")
    table.add_column("Similarity", style="white", justify="center")
    table.add_column("Where", justify="center")

    if len(matches) == 0:
        msg.warn("No matches found!", exits=1)

    for match in matches:
        is_local = match[0] in local_projects
        table.add_row(
            match[0],
            str(match[1]),
            "Local" if is_local else "Remote",
            style="green" if is_local else "dark_orange",
        )

    console = Console()
    console.print(table)
