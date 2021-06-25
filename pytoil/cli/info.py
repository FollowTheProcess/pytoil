"""
The pytoil info command.

Author: Tom Fleet
Created: 25/06/2021
"""

import httpx
import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.exceptions import RepoNotFoundError
from pytoil.repo import Repo

app = typer.Typer()


@app.command()
def info(
    project: str = typer.Argument(..., help="Name of the project to fetch info for.")
) -> None:
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
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )

    try:
        _ = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)

    try:
        with msg.loading(f"Fetching info for {project!r}..."):
            info_dict = repo.info(api=api)

    except RepoNotFoundError:
        msg.warn(
            f"{project!r} not found locally or on GitHub. Was it a typo?",
            spaced=True,
            exits=1,
        )
    else:
        typer.secho(f"\nInfo for {project!r}:\n", fg=typer.colors.CYAN, bold=True)
        for key, val in info_dict.items():
            typer.echo(f"{key}: {val}")
