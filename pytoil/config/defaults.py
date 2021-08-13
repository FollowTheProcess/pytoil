"""
Global defaults for pytoil.

Author: Tom Fleet
Created: 18/06/2021
"""


import os
from pathlib import Path
from typing import List, Set

# Default path for pytoil's config file
CONFIG_FILE: Path = Path.home().joinpath(".pytoil.yml").resolve()

# Valid pytoil config keys
CONFIG_KEYS: Set[str] = {
    "projects_dir",
    "token",
    "username",
    "vscode",
    "common_packages",
    "init_on_new",
}

# Pytoil docs URL
PYTOIL_DOCS_URL: str = "https://followtheprocess.github.io/pytoil/"

# Defaults for pytoil config
PROJECTS_DIR: Path = Path.home().joinpath("Development").resolve()
TOKEN: str = os.getenv("GITHUB_TOKEN", "")
USERNAME: str = ""
VSCODE: bool = False
COMMON_PACKAGES: List[str] = []
INIT_ON_NEW: bool = True

# Config Schema
CONFIG_SCHEMA = """

# The .pytoil.yml config file

## projects_dir *(bool)*

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

## common_packages *(List[str])*

A list of python packages to inject into every virtual environment pytoil creates
(e.g. linters, formatters and other dev dependencies).

Any versioning syntax (e.g. mypy>=0.902) will work as expected here as these packages
are passed straight through to installation tools like pip and conda.

## init_on_new *(bool)*

Whether or not you want pytoil to create an empty git repo when you make a new project with
'pytoil new'. This can also be disabled on a per use basis using the '--no-git' flag.
"""
