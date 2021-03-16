"""
Main CLI module.

Author: Tom Fleet
Created: 24/02/2021
"""

import pathlib
import shutil
from enum import Enum
from typing import Set

import typer
from cookiecutter.main import cookiecutter

from pytoil import __version__
from pytoil.cli import config, show, sync
from pytoil.cli.utils import env_dispatcher, get_local_project_set
from pytoil.config import CONFIG_PATH, Config
from pytoil.environments import CondaEnv, VirtualEnv
from pytoil.exceptions import (
    InvalidConfigError,
    RepoNotFoundError,
    VirtualenvAlreadyExistsError,
)
from pytoil.repo import Repo
from pytoil.vscode import VSCode

# Add all the subcommands
app = typer.Typer(name="pytoil", no_args_is_help=True)
app.add_typer(config.app, name="config")
app.add_typer(sync.app, name="sync")
app.add_typer(show.app, name="show")


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit()


# Callback for documentation only
@app.callback()
def main(
    version: bool = typer.Option(
        None,
        "--version",
        "-V",
        help="Display pytoil version.",
        callback=version_callback,
        is_eager=True,
        show_default=False,
    )
) -> None:
    """
    Helpful CLI to automate the development workflow.

    - Create and manage your local and remote projects

    - Build projects from cookiecutter templates.

    - Easily create/manage virtual environments.

    - Minimal configuration required.
    """


@app.command()
def init() -> None:
    """
    Initialise pytoil.

    Will guide user through the config setup
    interactively.
    """

    typer.secho("Checking for config file...\n", fg=typer.colors.BLUE, bold=True)

    # Make config file
    if not CONFIG_PATH.exists():
        try:
            typer.secho("No config file found!\n", fg=typer.colors.YELLOW)
            typer.echo("Creating fresh config file...\n")
            CONFIG_PATH.touch()
            default_config = Config()
            default_config.write()

            username: str = typer.prompt("GitHub username")
            token: str = typer.prompt("GitHub personal access token")
            projects_dir: str = typer.prompt("Absolute path to your projects directory")
            vscode: str = typer.prompt("Use VSCode to open projects with? [True|False]")

            projects_dir_path = pathlib.Path(projects_dir)

            if vscode.lower() == "true":
                vscode_bool = True
            elif vscode.lower() == "false":
                vscode_bool = False
            else:
                raise typer.BadParameter("VSCode must be a boolean value")

            user_config = Config(
                username=username,
                token=token,
                projects_dir=projects_dir_path,
                vscode=vscode_bool,
            )
            user_config.write()

            typer.secho("Config written, you're good to go!", fg=typer.colors.GREEN)
        except KeyboardInterrupt:
            # TODO: How to test this?
            # User pressed ctrl+c
            # Delete any created config file and gracefully exit
            typer.secho("Exiting config process...", fg=typer.colors.YELLOW)
            CONFIG_PATH.unlink(missing_ok=True)
            raise typer.Abort()
    else:
        try:
            config = Config.get()
            config.validate()
        except InvalidConfigError:
            typer.secho(
                "Something's wrong in the config file, please check it.\n",
                fg=typer.colors.RED,
            )
            typer.echo("If in doubt, simply delete it and run '$ pytoil init' again :)")
            raise typer.Abort()
        else:
            typer.secho("You're all set!", fg=typer.colors.GREEN)


class Venv(str, Enum):
    """
    Choice of virtualenvs to create in a new project.
    """

    virtualenv = "virtualenv"
    conda = "conda"


@app.command()
def create(
    project: str = typer.Argument(..., help="Name of the project to create."),
    cookie: str = typer.Option(
        None,
        "--cookie",
        "-c",
        help="URL to a cookiecutter template repo from which to create the project.",
    ),
    venv: Venv = typer.Option(
        None,
        "--venv",
        "-v",
        help="Which type of virtual environment to create for the project.",
        case_sensitive=False,
        show_default=True,
    ),
) -> None:
    """
    Create a new development project locally.

    If cookiecutter is specified it must be followed by a url to a
    valid cookiecutter template repo from which to construct the project.

    If you have url abbreviations configured for cookiecutter, these
    will work as expected.

    If cookiecutter not specified, pytoil will simply create an empty project
    directory named PROJECT in your configured location.

    If venv is specified, it must be one of "virtualenv" or "conda" and the
    corresponding environment will be created for your project. If venv is not
    specified, environment creation will be skipped.

    You must have the conda package manager installed on your system to create conda
    environments. The conda environment will have the same name as your project. The
    virtualenv environment will be located in the root of your project under the folder
    '.venv'.

    Examples:

    $ pytoil create my_project

    $ pytoil create my_project -c https://github.com/me/my_cookie_template.git

    $ pytoil create my_project -v conda -c https://github.com/me/cookie.git
    """

    # Everything below requires a valid config
    config = Config.get()
    config.validate()

    # Create the project repo object
    # And the VSCode object
    repo = Repo(name=project)
    if config.vscode:
        vscode = VSCode(root=repo.path)

    if repo.exists_local():
        typer.secho(
            f"\nProject: {project!r} already exists locally at '{repo.path}'.\n",
            fg=typer.colors.YELLOW,
        )
        typer.echo("To resume an existing project, use 'checkout'.")
        typer.echo(f"Example: '$ pytoil checkout {project}'.")
        raise typer.Abort()
    elif repo.exists_remote():
        typer.secho(
            f"\nProject: {project!r} already exists on GitHub.\n",
            fg=typer.colors.YELLOW,
        )
        typer.echo("To resume an existing project, use 'checkout'.")
        typer.echo(f"Example: '$ pytoil checkout {project}'.")
        raise typer.Abort()

    # If we get here, project is okay to create

    if cookie:
        typer.secho(
            f"\nCreating project: {project!r} with cookiecutter template:"
            + f" {cookie!r}.\n",
            fg=typer.colors.BLUE,
            bold=True,
        )
        cookiecutter(template=cookie, output_dir=config.projects_dir)
    else:
        typer.secho(
            f"\nCreating project: {project!r} at '{repo.path}'.\n",
            fg=typer.colors.BLUE,
            bold=True,
        )
        # Create an empty project dir
        repo.path.mkdir()

    if venv:
        if venv.value == venv.conda:
            typer.secho(
                f"Creating conda environment for {project!r}.\n",
                fg=typer.colors.BLUE,
                bold=True,
            )
            conda_env = CondaEnv(name=project, project_path=repo.path)
            try:
                conda_env.create()
            except VirtualenvAlreadyExistsError:
                typer.echo(f"Conda environment: {conda_env.name!r} already exists!")
                typer.echo(f"Using {conda_env.name!r} as the environment.")
            finally:
                if config.vscode:
                    typer.echo("\nSetting 'python.pythonPath' in VSCode workspace.\n")
                    vscode.set_python_path(conda_env.executable)
                    typer.echo(f"Opening {project!r} in VSCode...")
                    vscode.open()

        elif venv.value == venv.virtualenv:  # pragma: no cover
            # For some reason coverage isn't picking this up as tested
            # but it is: tests/cli/test_project_create.py
            # in several tests
            typer.secho(
                f"Creating virtualenv for {project!r}.\n",
                fg=typer.colors.BLUE,
                bold=True,
            )

            env = VirtualEnv(project_path=repo.path)
            env.create()

            typer.echo(
                "\nEnsuring seed packages (pip, setuptools, wheel) are up to date."
            )
            env.update_seeds()

            if config.vscode:
                typer.echo("\nSetting 'python.pythonPath' in VSCode workspace.\n")
                vscode.set_python_path(env.executable)
                typer.echo(f"Opening {project!r} in VSCode...")
                vscode.open()
    else:
        typer.echo("Virtual environment not requested. Skipping environment creation.")
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    typer.secho("\nDone!", fg=typer.colors.GREEN)


@app.command()
def checkout(
    project: str = typer.Argument(..., help="Name of the project to checkout.")
) -> None:
    """
    Checkout a development project, either locally or from GitHub.

    pytoil will first check your configured projects directory
    for a matching name, falling back to searching your GitHub repositories.

    If checkout finds the project locally, it will ensure any virtual environments
    are configured properly if required (e.g. a python project) and open the
    root of the project in your chosen editor.

    If checkout finds a match, not locally but in your GitHub repos, it will
    first clone the repo to your projects directory before proceeding as if
    it existed locally.

    If neither of these finds a match, an error message will be shown.

    Examples:

    $ pytoil checkout my_cool_project
    """

    # Everything below requires a valid config
    config = Config.get()
    config.validate()

    # Project exists either locally or on users GitHub
    # and is to be grabbed by name only
    repo = Repo(name=project)
    if config.vscode:
        vscode = VSCode(root=repo.path)

    if repo.exists_local():
        # Note we don't do any environment stuff here
        # chances are if it exists locally, this has already been done
        typer.secho(
            f"\nProject: {project!r} is available locally at" f" '{repo.path}'.\n",
            fg=typer.colors.BLUE,
            bold=True,
        )
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    elif repo.exists_remote():
        typer.secho(
            f"Project: {project!r} found on your GitHub. Cloning...\n",
            fg=typer.colors.BLUE,
            bold=True,
        )
        repo.clone()
        env = env_dispatcher(repo)
        if not env:
            typer.secho(
                "\nUnable to auto-detect virtual environment. Skipping.",
                fg=typer.colors.YELLOW,
            )
        else:
            typer.echo("\nAuto-creating correct virtual environment...\n")
            try:
                env.create()
            except VirtualenvAlreadyExistsError:
                typer.echo(
                    "Matching environment already exists. No need to create a new one!"
                )
            finally:
                if config.vscode:
                    typer.echo("Setting 'python.pythonPath' in VSCode workspace...\n")
                    vscode.set_python_path(env.executable)

        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    else:
        typer.secho(
            f"Project: {project!r} not found locally or on your GitHub.\n",
            fg=typer.colors.RED,
        )
        typer.echo(
            "Does the project exist? If not, create a new project:"
            + f" '$ pytoil create {project}'."
        )
        raise typer.Abort()


@app.command()
def remove(
    project: str = typer.Argument(..., help="Name of the project to remove."),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Remove project without prompting for confirmation.",
        show_default=False,
    ),
) -> None:
    """
    Deletes a project from your local filesystem.

    Deletion is done recursively, roughly equivalent to '$ rm -r {project}'.

    User will be prompted for confirmation unless "--force/-f" flag is used.

    Examples:

    $ pytoil remove my_project

    $ pytoil remove --force my_project
    """

    # Everything below needs a valid config
    config = Config.get()
    config.validate()

    # Set because we don't care about sorting
    # but we want fast membership checking
    local_projects: Set[str] = get_local_project_set(config.projects_dir)

    if project not in local_projects:
        typer.secho(
            f"Project: {project!r} not found in local filesystem.", fg=typer.colors.RED
        )
        raise typer.Abort()

    if not force:
        # Confirm with user and abort if they say no
        typer.confirm(
            f"\nThis will remove {project!r} from your local filesystem."
            + " Are you sure?",
            abort=True,
        )

    # If user specifies force flag, just go ahead and remove
    typer.secho(f"\nRemoving project: {project!r}.", fg=typer.colors.YELLOW)
    shutil.rmtree(config.projects_dir.joinpath(project))
    typer.secho("\nDone!", fg=typer.colors.GREEN)


@app.command()
def info(
    project: str = typer.Argument(..., help="Name of the project to fetch info for.")
) -> None:
    """
    Show useful information about a project.

    If the requested project is local only, a
    small subset of info will be shown to do with
    the local directory.

    However if the project is available on GitHub
    a more comprehensive info set is shown.

    Examples:

    $ pytoil info my_project
    """

    config = Config.get()
    config.validate()

    repo = Repo(name=project)

    try:
        info_dict = repo.info()
    except RepoNotFoundError:
        typer.secho(
            f"Project: {project!r} not found locally or on GitHub.", fg=typer.colors.RED
        )
        raise typer.Abort()
    else:
        typer.secho(f"\nInfo for: {project!r}\n", fg=typer.colors.BLUE, bold=True)
        for key, val in info_dict.items():
            typer.echo(f"{key}: {val}")
