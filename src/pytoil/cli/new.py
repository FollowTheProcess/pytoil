"""
The pytoil new command.


Author: Tom Fleet
Created: 21/12/2021
"""

from __future__ import annotations

import asyncio
import functools

import aiofiles.os
import asyncclick as click
from cookiecutter.main import cookiecutter

from pytoil import editor
from pytoil.api import API
from pytoil.cli.printer import printer
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
    type=click.Choice(choices=("python", "go", "rust"), case_sensitive=True),
    help="Use a language-specific starter template.",
)
@click.option(
    "-v",
    "--venv",
    type=click.Choice(choices=("venv", "conda"), case_sensitive=True),
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
    this behaviour by setting 'git' to false in pytoil's config file
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
    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )
    git = Git()

    # Additional packages to include
    to_install: list[str] = [*packages] + config.common_packages

    # Can't use --cookie and --starter
    if cookie and starter:
        printer.error("--cookie and --starter are mutually exclusive", exits=1)

    # Can't use --venv with non-python starters
    if (
        starter is not None  # User specified --starter
        and starter != "python"  # Requested starter is not python
        and venv is not None  # And the user wants a virtual environment
    ):
        printer.error(f"Can't create a venv for a {starter} project", exits=1)

    # Resolve config vs flag for no-git
    # flag takes priority over config
    use_git: bool = config.git and not no_git

    # Does this project already exist?
    # Mightaswell check concurrently
    local, remote = await asyncio.gather(repo.exists_local(), repo.exists_remote(api))

    if local:
        printer.error(f"{repo.name} already exists locally.")
        printer.note(
            f"To checkout this project, use `pytoil checkout {repo.name}`.", exits=1
        )

    if remote:
        printer.error(f"{repo.name} already exists on GitHub.")
        printer.note(
            f"To checkout this project, use `pytoil checkout {repo.name}`.", exits=1
        )

    # If we get here, we're good to create a new project
    if cookie:
        printer.info(f"Creating {repo.name} from cookiecutter: {cookie}.")
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            executor=None,
            func=functools.partial(
                cookiecutter,
                template=cookie,
                output_dir=str(config.projects_dir),
            ),
        )

    elif starter == "go":
        printer.info(f"Creating {repo.name} from starter: {starter}.")
        go_starter = GoStarter(path=config.projects_dir, name=repo.name)

        try:
            await go_starter.generate(username=config.username)
        except GoNotInstalledError:
            printer.error("Go not installed.", exits=1)
        else:
            if use_git:
                await git.init(cwd=repo.local_path, silent=False)
                await git.add(cwd=repo.local_path, silent=False)
                await git.commit(cwd=repo.local_path, silent=False)

    elif starter == "python":
        printer.info(f"Creating {repo.name} from starter: {starter}.")
        python_starter = PythonStarter(path=config.projects_dir, name=repo.name)
        await python_starter.generate()
        if use_git:
            await git.init(cwd=repo.local_path, silent=False)
            await git.add(cwd=repo.local_path, silent=False)
            await git.commit(cwd=repo.local_path, silent=False)

    elif starter == "rust":
        printer.info(f"Creating {repo.name} from starter: {starter}.")
        rust_starter = RustStarter(path=config.projects_dir, name=repo.name)

        try:
            await rust_starter.generate()
        except CargoNotInstalledError:
            printer.error("Cargo not installed.", exits=1)
        else:
            if use_git:
                await git.init(cwd=repo.local_path, silent=False)
                await git.add(cwd=repo.local_path, silent=False)
                await git.commit(cwd=repo.local_path, silent=False)

    else:
        # Just a blank new project
        printer.info(f"Creating {repo.name} at '{repo.local_path}'.")
        await aiofiles.os.mkdir(repo.local_path)
        if use_git:
            await git.init(cwd=repo.local_path, silent=False)

    # Now we need to handle any requested virtual environments
    if venv == "venv":
        printer.info(f"Creating virtual environment for {repo.name}")
        if to_install:
            printer.note(f"Including {', '.join(to_install)}")

        env = Venv(root=repo.local_path)
        with printer.progress() as p:
            p.add_task("[bold white]Working")
            await env.create(packages=to_install, silent=True)

    elif venv == "conda":
        # Note, conda installs take longer so by default we don't hide the output
        # like we do for normal python environments
        printer.info(f"Creating conda environment for {repo.name}")
        if to_install:
            printer.note(f"Including {', '.join(to_install)}")

        conda_env = Conda(
            root=repo.local_path, environment_name=repo.name, conda=config.conda_bin
        )
        try:
            await conda_env.create(packages=to_install)
        except EnvironmentAlreadyExistsError:
            printer.error(
                f"Conda environment {conda_env.environment_name!r} already exists",
                exits=1,
            )
        else:
            # Export the environment.yml
            await conda_env.export_yml()

    # Now handle opening in an editor
    if config.specifies_editor():
        printer.info(f"Opening {repo.name} with {config.editor}", spaced=True)
        await editor.launch(path=repo.local_path, bin=config.editor)
