"""
The pytoil new command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncio

import aiofiles.os
import asyncclick as click
from cookiecutter.main import cookiecutter
from wasabi import msg

from pytoil.api import API
from pytoil.config import Config
from pytoil.environments import Conda, Venv
from pytoil.exceptions import (
    CargoNotInstalledError,
    EnvironmentAlreadyExistsError,
    GoNotInstalledError,
)
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.starters import GoStarter, PythonStarter, RustStarter
from pytoil.vscode import VSCode


@click.command()
@click.argument("project", nargs=1, type=str)
@click.argument("packages", nargs=-1)
@click.option(
    "-c",
    "--cookie",
    type=str,
    help="URL to a cookiecutter template from which to build the project.",
)
@click.option(
    "-s",
    "--starter",
    type=click.Choice(choices={"python", "go", "rust"}, case_sensitive=True),
    help="Use a language-specific starter template.",
)
@click.option(
    "-v",
    "--venv",
    type=click.Choice(choices={"venv", "conda"}, case_sensitive=True),
    help="Which type of virtual environment to create.",
)
@click.option(
    "-n",
    "--no-git",
    is_flag=True,
    default=False,
    help="Don't do any git stuff.",
)
@click.pass_obj
async def new(  # noqa: C901
    config: Config,
    project: str,
    packages: tuple[str, ...],
    cookie: str | None,
    starter: str | None,
    venv: str | None,
    no_git: bool = False,
) -> None:
    """
    Create a new development project.

    Bare usage will simply create an empty folder in your configured projects
    directory.

    You can also create a project from a cookiecutter template by passing a valid
    url to the '--cookie/-c' flag.

    If you just want a very simple, language-specific starting template, use the
    '--starter/-s' option.

    By default, pytoil will initialise a local git repo in the folder and commit it,
    following the style of modern language build tools such as rust's cargo. You can disable
    this behaviour by setting 'init_on_new' to false in pytoil's config file
    or by passing the '--no-git/-n' flag here.

    If you want pytoil to create a new virtual environment for your project, you
    can use the '--venv/-v' flag. Standard python and conda virtual environments
    are supported.

    If the '--venv/-v' flag is used, you may also pass a list of python packages
    to install into the created virtual environment. These will be delegated to
    the appropriate tool (pip or conda) depending on what environment was created.
    If the environment is conda, the packages will be passed at environment creation
    time meaning they will have their dependencies resolved together. Normal python
    environments will first be created and then have specified packages installed.

    If 'common_packages' is specified in pytoil's config file, these will automatically
    be included in the environment.

    To specify versions of packages via the command line, you must enclose them
    in double quotes e.g. "flask>=1.0.0" not flask>=1.0.0 otherwise this will
    be interpreted by the shell as a command redirection.

    Examples:

    $ pytoil new my_project

    $ pytoil new my_project --cookie https://github.com/some/cookie.git

    $ pytoil new my_project --venv conda

    $ pytoil new my_project -c https://github.com/some/cookie.git -v conda --no-git

    $ pytoil new my_project -v venv requests "flask>=1.0.0"

    $ pytoil new my_project --starter python
    """
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
    code = VSCode(root=repo.local_path, code=config.code_bin)
    git = Git()

    # Additional packages to include
    to_install: list[str] = [*packages] + config.common_packages

    # Can't use --cookie and --starter
    if cookie and starter:
        msg.warn("--cookie and --starter are mutually exclusive", exits=1)

    # Can't use --venv with non-python starters
    if (
        starter is not None  # User specified --starter
        and starter != "python"  # Requested starter is not python
        and venv is not None  # And the user wants a virtual environment
    ):
        msg.warn(f"Can't create a venv for a {starter} project", exits=1)

    # Resolve config vs flag for no-git
    # flag takes priority over config
    use_git: bool = config.init_on_new and not no_git

    # Does this project already exist?
    # Mightaswell check concurrently
    local, remote = await asyncio.gather(repo.exists_local(), repo.exists_remote(api))

    if local:
        msg.warn(
            title=f"{repo.name} already exists locally.",
            text=f"To checkout this project, use 'pytoil checkout {repo.name}'.",
            exits=1,
        )

    if remote:
        msg.warn(
            title=f"{repo.name} already exists on GitHub.",
            text=f"To checkout this project, use 'pytoil checkout {repo.name}'.",
            exits=1,
        )

    # If we get here, we're good to create a new project
    if cookie:
        msg.info(f"Creating {repo.name!r} from cookiecutter: {cookie!r}.")
        cookiecutter(template=cookie, output_dir=repo.name)

    elif starter == "go":
        msg.info(f"Creating {repo.name!r} from starter: {starter!r}.")
        go_starter = GoStarter(path=config.projects_dir, name=repo.name)

        try:
            await go_starter.generate(username=config.username)
        except GoNotInstalledError:
            msg.fail("Error: Go not installed.", exits=1)
        else:
            if use_git:
                await git.init(cwd=repo.local_path, silent=False)
                await git.add(cwd=repo.local_path, silent=False)
                await git.commit(cwd=repo.local_path, silent=False)

    elif starter == "python":
        msg.info(f"Creating {repo.name!r} from starter: {starter!r}.")
        python_starter = PythonStarter(path=config.projects_dir, name=repo.name)
        await python_starter.generate()
        if use_git:
            await git.init(cwd=repo.local_path, silent=False)
            await git.add(cwd=repo.local_path, silent=False)
            await git.commit(cwd=repo.local_path, silent=False)

    elif starter == "rust":
        msg.info(f"Creating {repo.name!r} from starter: {starter!r}.")
        rust_starter = RustStarter(path=config.projects_dir, name=repo.name)

        try:
            await rust_starter.generate()
        except CargoNotInstalledError:
            msg.fail("Error: Cargo not installed.", exits=1)
        else:
            if use_git:
                await git.init(cwd=repo.local_path, silent=False)
                await git.add(cwd=repo.local_path, silent=False)
                await git.commit(cwd=repo.local_path, silent=False)

    else:
        # Just a blank new project
        msg.info(f"Creating {repo.name!r} at {repo.local_path}.")
        await aiofiles.os.mkdir(repo.local_path)
        if use_git:
            await git.init(cwd=repo.local_path, silent=False)

    # Now we need to handle any requested virtual environments
    if venv == "venv":
        msg.info(
            title=f"Creating virtual environment for {repo.name!r}",
            text=f"Including packages: {', '.join(to_install)}" if to_install else "",
        )
        env = Venv(root=repo.local_path)
        with msg.loading("Working..."):
            await env.create(packages=to_install, silent=True)

    elif venv == "conda":
        msg.info(
            title=f"Creating conda environment for {repo.name!r}",
            text=f"Including packages: {', '.join(to_install)}" if to_install else "",
        )
        conda_env = Conda(root=repo.local_path, environment_name=repo.name)
        try:
            await conda_env.create(packages=to_install)
        except EnvironmentAlreadyExistsError:
            msg.fail(
                f"Conda environment: {conda_env.environment_name!r} already exists",
                exits=1,
            )
        else:
            # Export the environment.yml
            await conda_env.export_yml()

    # Now handle opening in VSCode
    if config.vscode:
        msg.info(f"Opening {repo.name!r} in VSCode.")
        await code.open()
