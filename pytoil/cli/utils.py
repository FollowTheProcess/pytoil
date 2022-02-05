"""
Collection of useful helpers for the CLI.


Author: Tom Fleet
Created: 30/12/2021
"""
from __future__ import annotations

import httpx

from pytoil.cli.printer import printer


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
        printer.error("HTTP 401 - Unauthorized")
        printer.note("This usually means something is wrong with your token!", exits=1)
    elif code == 404:
        printer.error("HTTP 404 - Not Found")
        printer.note("This is a bug we've not handled, please raise an issue!", exits=1)
    elif code == 500:
        printer.error("HTTP 500 - Server Error")
        printer.note("This is very rare but it means GitHub is not happy!", exits=1)
