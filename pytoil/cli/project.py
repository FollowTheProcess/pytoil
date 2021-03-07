"""
CLI project command.

Author: Tom Fleet
Created: 24/02/2021
"""

import shutil
from enum import Enum
from typing import Set

import typer
from cookiecutter.main import cookiecutter

from pytoil.config import Config
from pytoil.environments import CondaEnv, VirtualEnv
from pytoil.repo import Repo
from pytoil.vscode import VSCode


class Venv(str, Enum):
    """
    Choice of virtualenvs to create in a new project.
    """

    virtualenv = "virtualenv"
    conda = "conda"
    none = "none"


app = typer.Typer(no_args_is_help=True)


# Callback for documentation only
@app.callback()
def project() -> None:
    """
    Operate on a specific project.

    Set the "projects_dir" key in the config to control
    where this command looks on your local file system.

    Set the "token" key in the config to give pytoil access
    to your GitHub via the API.

    We only make GET requests, your repos are safe with pytoil!
    """


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
        Venv.none,
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

    $ pytoil project create my_project

    $ pytoil project create my_project -c https://github.com/me/my_cookie_template.git

    $ pytoil project create my_project -v conda -c https://github.com/me/cookie.git
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
            f"\nProject: {project!r} already exists locally at '{repo.path}'.",
            fg=typer.colors.YELLOW,
        )
        typer.echo("To resume an existing project, use 'checkout'.")
        typer.echo(f"Example: '$ pytoil project checkout {project}'.")
        raise typer.Abort()

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

    if venv.value == venv.conda:
        typer.secho(
            f"\nCreating conda environment for {project!r}.\n",
            fg=typer.colors.BLUE,
            bold=True,
        )
        conda_env = CondaEnv(name=project)
        conda_env.create()

        typer.echo("\nExporting 'environment.yml' file.")
        conda_env.export_yml(fp=repo.path)
        # TODO: Also open code and set pythonPath
        # will need some way of autodetermining the users
        # conda envs directory
        # parsing the return from conda info will probably do it

    elif venv.value == venv.virtualenv:
        typer.secho(
            f"\nCreating virtualenv for {project!r}.\n",
            fg=typer.colors.BLUE,
            bold=True,
        )

        env = VirtualEnv(basepath=repo.path)
        env.create()

        typer.echo("\nEnsuring seed packages (pip, setuptools, wheel) are up to date.")
        env.update_seeds()

        if config.vscode:
            typer.echo("Setting 'python.pythonPath' in VSCode workspace.")
            vscode.set_python_path(python_path=env.executable)  # type: ignore
            # we ignore type here because by this point we know env.executable
            # cannot be None
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()

    elif venv.value == venv.none:
        typer.echo("Virtual environment not requested. Skipping environment creation.")
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode...")
            vscode.open()
    else:
        # This should never happen as we're using an Enum
        # But just incase, let's abort
        typer.secho("Unrecognised option for venv.", fg=typer.colors.RED)
        raise typer.Abort()

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

    $ pytoil project checkout my_cool_project
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
        typer.secho(
            f"\nProject: {project!r} is already available locally at"
            f" '{repo.path}'.",
            fg=typer.colors.GREEN,
        )
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode.")
            vscode.open()
    elif repo.exists_remote():
        typer.echo(f"Project: {project!r} found on user's GitHub. Cloning...\n")
        repo.clone()
        typer.secho(
            f"Project: {project!r} now available locally at" f" '{repo.path}'.",
            fg=typer.colors.GREEN,
        )
        if config.vscode:
            typer.echo(f"Opening {project!r} in VSCode.")
            vscode.open()
    else:
        typer.secho(
            f"Project: {project!r} not found on user's GitHub.\n",
            fg=typer.colors.RED,
        )
        typer.echo(
            "Does the project exist? If not, create a new project:"
            + f" '$ pytoil project create {project}'."
        )


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

    Example

    $ pytoil project remove my_project

    $ pytoil project remove --force my_project
    """

    # Everything below needs a valid config
    config = Config.get()
    config.validate()

    # Set because we don't care about sorting
    # but we want fast membership checking
    local_projects: Set[str] = {
        f.name
        for f in config.projects_dir.iterdir()
        if f.is_dir() and not f.name.startswith(".")
    }

    if project not in local_projects:
        typer.secho(
            f"Project: {project!r} not found in local filesystem.", fg=typer.colors.RED
        )
        raise typer.Abort()

    if not force:
        # Confirm with user and abort if they say no
        typer.confirm(
            f"\nThis will remove {project!r} from your local filesystem."
            + " This is IRREVERSIBLE! Are you sure?",
            abort=True,
        )

        # If user said no, typer will abort and this statement will not run
        typer.secho(
            f"\nRemoving project: {project!r}.", fg=typer.colors.BLUE, bold=True
        )
        shutil.rmtree(config.projects_dir.joinpath(project))
        typer.secho("\nDone!", fg=typer.colors.GREEN)

    else:
        # If user specifies force flag, just go ahead and remove
        typer.secho(
            f"\nRemoving project: {project!r}.", fg=typer.colors.BLUE, bold=True
        )
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

    Example

    $ pytoil project info my_project
    """

    config = Config.get()
    config.validate()

    repo = Repo(name=project)

    info_dict = repo.info()

    typer.secho(f"\nInfo for: {project}\n", fg=typer.colors.BLUE, bold=True)
    for key, val in info_dict.items():
        typer.echo(f"{key}: {val}")
