"""
Collection of useful helpers for the CLI.


Author: Tom Fleet
Created: 30/12/2021
"""
from __future__ import annotations

import httpx
from wasabi import msg


def handle_http_status_error(error: httpx.HTTPStatusError) -> None:
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
            text="This usually means you've made a typo.",
            exits=1,
        )
    elif code == 500:
        msg.fail(
            title="HTTP Error: 500 - Internal Server Error",
            text="This usually means GitHub is not happy.",
            exits=1,
        )
