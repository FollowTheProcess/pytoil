"""
Global defaults for pytoil.

Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import os
from pathlib import Path

# Default path for pytoil's config file
CONFIG_FILE: Path = Path.home().joinpath(".pytoil.toml").resolve()

# Valid pytoil config keys
CONFIG_KEYS: set[str] = {
    "projects_dir",
    "token",
    "username",
    "vscode",
    "code_bin",
    "conda_bin",
    "cache_timeout",
    "common_packages",
    "git",
}

# API cache
CACHE_DIR = Path.home().joinpath(".cache/pytoil")
CACHE_TIMEOUT_SECS = 120


# Pytoil meta stuff
PYTOIL_DOCS_URL: str = "https://followtheprocess.github.io/pytoil/"
PYTOIL_ISSUES_URL: str = "https://github.com/FollowTheProcess/pytoil/issues"

# Defaults for pytoil config
PROJECTS_DIR: Path = Path.home().joinpath("Development").resolve()
TOKEN: str = os.getenv("GITHUB_TOKEN", "")
USERNAME: str = ""
VSCODE: bool = False
CODE_BIN: str = "code"
CONDA_BIN: str = "conda"
COMMON_PACKAGES: list[str] = []
GIT: bool = True

# Config Schema
CONFIG_SCHEMA = """

# The .pytoil.toml config file

## projects_dir *(str)*

The absolute path to where you keep your development projects
(e.g. /Users/you/Projects).

## token *(str)*

Your GitHub personal access token. This must have a minimum of repo read access. See the documentation here:
https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token

Pytoil will try and get this from the config file initially, then fall back to the $GITHUB_TOKEN environment
variable. If neither of these places are set, you will not be able to use pytoil commands that rely on the
GitHub API. Pytoil will notify you of this when any of these commands are called.

## username *(str)*

Your GitHub username. Pytoil needs this so it can construct urls to your projects.

## vscode *(bool)*

Whether you want pytoil to open projects up using VSCode. This will happen on 'new' and 'checkout'.

## code_bin *(str)*

The name of the VSCode binary. Will differ depending on version installed. Either "code" (default)
or "code-insiders"

## conda_bin *(str)*

The name of the binary to use when performing conda operations. Either "conda" (default)
or "mamba"

# cache_timeout *(int)*

The number of seconds pytoil keeps a cache of GitHub API requests for. Subsequent API calls
within this window will be served from cache not from the API.

## common_packages *(List[str])*

A list of python packages to inject into every virtual environment pytoil creates
(e.g. linters, formatters and other dev dependencies).

Any versioning syntax (e.g. mypy>=0.902) will work as expected here as these packages
are passed straight through to installation tools like pip and conda.

## git *(bool)*

Whether or not you want pytoil to create an empty git repo when you make a new project with
'pytoil new'. This can also be disabled on a per use basis using the '--no-git' flag.
"""
