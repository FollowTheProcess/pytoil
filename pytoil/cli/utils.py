"""
Assorted helper functions for the pytoil CLI.

Author: Tom Fleet
Created: 19/06/2021
"""

from pathlib import Path
from typing import Set

import httpx
from wasabi import msg

from pytoil.config import Config


def get_local_projects(path: Path) -> Set[str]:
    """
    Returns all the projects (directories) under
    `path`.
    """

    return {f.name for f in path.iterdir() if f.is_dir() and not f.name.startswith(".")}


def warn_if_no_api_creds(config: Config) -> None:
    """
    Will print a helpful warning message and exit the program
    if username or token are not filled out in the config file.
    """

    if not config.can_use_api():
        msg.warn(
            "You must fill set your username and token to use API features!",
            spaced=True,
            exits=1,
        )


def handle_http_status_errors(error: httpx.HTTPStatusError) -> None:
    """
    Handles a variety of possible HTTP Status errors, print's nicer output
    to the user, and exits the program if necessary.

    Call this in an except block on CLI commands accessing the
    GitHub API.

    Args:
        error (httpx.HTTPStatusError): The error to be handled.
    """
    code = error.response.status_code

    if code == 401:
        msg.fail(
            title="HTTP Error: 401 - Unauthorized",
            text="This usually means something is wrong with your token!",
            exits=1,
        )
    elif code == 404:
        msg.fail(
            title="HTTP Error: 404 - Not Found",
            text="This usually means something is up with the GitHub API.",
            exits=1,
        )
    elif code == 500:
        msg.fail(
            title="HTTP Error: 500 - Internal Server Error",
            text="This usually means GitHub is not happy.",
            exits=1,
        )
