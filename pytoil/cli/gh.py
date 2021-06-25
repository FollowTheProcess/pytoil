"""
The pytoil gh command.

Author: Tom Fleet
Created: 25/06/2021
"""

import httpx
import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.repo import Repo

app = typer.Typer()


@app.command()
def gh(
    project: str = typer.Argument(..., help="Name of the project to go to on GitHub.")
) -> None:  # pragma: no cover
    """
    Open one of your projects on GitHub.

    Given a project name (must exist on GitHub and be owned by you),
    'gh' will open your browser and navigate to the project on GitHub.

    Examples:

    $ pytoil gh my_project
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
        exists_remote = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        if not exists_remote:
            msg.warn(
                f"{project!r} not found on GitHub! Was it a typo?", spaced=True, exits=1
            )
        else:
            msg.info(f"Opening {project!r} on GitHub...", spaced=True)
            typer.launch(url=repo.html_url)
