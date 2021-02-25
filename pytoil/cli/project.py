"""
CLI project command.

Author: Tom Fleet
Created: 24/02/2021
"""

import shutil
from enum import Enum
from typing import List, Set

import typer
from cookiecutter.main import cookiecutter

from pytoil.api import API
from pytoil.config import Config
from pytoil.env import CondaEnv, VirtualEnv
from pytoil.repo import Repo


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
    Manage your local and remote development projects.

    Set the "projects_dir" key in the config to control
    where this command looks on your local file system.

    Set the "token" key in the config to give pytoil access
    to your GitHub via the API.
    """


@app.command()
def create(
    project: str = typer.Argument(..., help="Name of the project to create."),
    cookie: str = typer.Option(
        None,
        "--cookiecutter",
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
    Create a new development project.

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
    config.raise_if_unset()

    # Create the project repo object
    repo = Repo(name=project)

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

    elif venv.value == venv.virtualenv:
        typer.secho(
            f"\nCreating virtualenv environment for {project!r}.\n",
            fg=typer.colors.BLUE,
            bold=True,
        )

        env = VirtualEnv(basepath=repo.path)
        env.create()

        typer.echo("\nEnsuring seed packages (pip, setuptools, wheel) are up to date.")
        env.update_seeds()

    elif venv.value == venv.none:
        typer.echo("Virtual environment not requested. Skipping environment creation.")
    else:
        # This should never happen as we're using an Enum
        # But just incase, let's abort
        typer.secho("Unrecognised option for venv.", fg=typer.colors.RED)
        raise typer.Abort()

    typer.secho("\nDone!", fg=typer.colors.GREEN)


@app.command()
def checkout(
    project: str = typer.Argument(
        default=None, help="Name of the project to checkout."
    ),
    url: str = typer.Option(
        None,
        "--url",
        "-u",
        help="URL of a project to checkout (skips searching).",
    ),
    path: str = typer.Option(
        None,
        "--path",
        "-p",
        help="Shorthand repo path of a project to checkout (skips searching).",
    ),
) -> None:
    """
    Checkout a development project, either locally or from GitHub.

    pytoil will first check your configured projects directory
    for a matching name, falling back to searching your GitHub repositories,
    and finally asking you to specify what project you want to checkout work on.
    e.g. if you want to work on a new repo owned by someone else.

    If checkout finds the project locally, it will ensure any virtual environments
    are configured properly if required (e.g. a python project) and open the
    root of the project in your chosen editor.

    If checkout finds a match, not locally but in your GitHub repos, it will
    first clone the repo to your projects directory before proceeding as if
    it existed locally.

    If neither of these finds a match, you will be asked to specify a url
    to a GitHub repo of the project you want to work on.

    You can also specify this at the beginning with the "-u/--url"
    or "-p/--path" options.

    If either of these are specified, the local and remote repo searching is skipped
    and the specified repo will be forked and cloned.

    Examples:

    $ pytoil project checkout my_cool_project

    $ pytoil project checkout --url https://github.com/someone/their_cool_project.git

    $ pytoil project checkout --path someone/their_cool_project
    """

    # Everything below requires a valid config
    config = Config.get()
    config.raise_if_unset()

    if url or path:

        # Guard against invalid usage
        if url and path:
            raise typer.BadParameter("'--url' and '--path' cannot be used together.")
        elif project:
            raise typer.BadParameter(
                "Arg: PROJECT cannot be used with either '--url' or '--path'."
            )

        # Meaning most likely it's not the users repo
        # url or path will both use the same logic
        # configure the repo object upfront with either url or path
        if url:
            typer.secho(
                f"\nResuming project from url: {url!r}.",
                fg=typer.colors.BLUE,
                bold=True,
            )
            repo = Repo.from_url(url=url)
        elif path:
            typer.secho(
                f"\nResuming project from path: {path!r}.",
                fg=typer.colors.BLUE,
                bold=True,
            )
            repo = Repo.from_path(path=path)

        # Now handle all the clone/fork logic
        if repo.owner == config.username:
            # i.e. the requested repo belongs to the user
            typer.echo(f"It looks like you own the repo: '{repo.owner}/{repo.name}'.")
            typer.echo(
                "FYI: You could have just said: "
                + f"'$ pytoil project checkout {repo.name}'."
            )
            if not repo.exists_local():
                typer.echo(f"Cloning '{repo.owner}/{repo.name}'.")
                repo.clone()
                typer.secho(
                    f"\nProject: {project!r} now available locally at '{repo.path}'.",
                    fg=typer.colors.GREEN,
                )
                # TODO: Handle project setup actions e.g. virtualenvs, determine
                # which env from file content
            else:
                typer.secho(
                    f"\nProject: {project!r} already available at '{repo.path}'.",
                    fg=typer.colors.GREEN,
                )
        else:
            # Requested repo does not belong to the user
            # NOTE: No cloning is done here because forking is
            # asynchronous meaning we might not have anything to clone
            # at execution time
            # Instead we report that to the user and ask them to clone
            # by using 'checkout' in a few moments.
            typer.echo(
                f"It looks like the repo: '{repo.owner}/{repo.name}' isn't yours."
            )
            if repo.exists_remote():
                typer.secho(
                    f"\nCreating fork: '{config.username}/{repo.name}'\n",
                    fg=typer.colors.BLUE,
                    bold=True,
                )
                user_fork = repo.fork()
                typer.secho(
                    f"Your fork: {user_fork!r} has been requested.\n",
                    fg=typer.colors.GREEN,
                )
                typer.echo(
                    "FYI: Forking happens asynchronously so your fork may not be"
                    + " available to clone for a few moments."
                    + " It's best to wait for 30 seconds or so"
                    + f" then run '$ pytoil project checkout {project}'."
                )
            else:
                typer.secho(
                    f"Repo: '{repo.owner}/{repo.name}' not found on GitHub.",
                    fg=typer.colors.RED,
                )
                raise typer.Abort()
    else:
        # Project exists either locally or on users GitHub
        # and is to be grabbed by name only
        if not project:
            typer.secho(
                "If not checking out from a url or path"
                + ", you must specify a project name.",
                fg=typer.colors.YELLOW,
            )
            raise typer.Abort()
        else:
            # We have a project name
            typer.secho(
                f"\nResuming project: {project!r}\n", fg=typer.colors.BLUE, bold=True
            )

            repo = Repo(name=project)

            if repo.exists_local():
                typer.secho(
                    f"\nProject: {project!r} is already available locally at"
                    f" '{repo.path}'.",
                    fg=typer.colors.GREEN,
                )
            else:
                typer.secho(
                    f"\nProject: {project!r} not found locally."
                    + " Checking user's GitHub...\n",
                    fg=typer.colors.YELLOW,
                )
                if repo.exists_remote():
                    typer.echo(
                        f"Project: {project!r} found on user's GitHub. Cloning...\n"
                    )
                    repo.clone()
                    typer.secho(
                        f"Project: {project!r} now available locally at"
                        f" '{repo.path}'.",
                        fg=typer.colors.GREEN,
                    )
                else:
                    typer.secho(
                        f"Project: {project!r} not found on user's GitHub.\n",
                        fg=typer.colors.RED,
                    )
                    typer.echo(
                        "Does the project exist? If not, create a new project:"
                        + f" '$ pytoil project create {project}'."
                    )
                    typer.echo(
                        "Or specify a url/path to a repo directly with the "
                        + "--url/--path option"
                    )


@app.command()
def list(
    remote: bool = typer.Option(
        False,
        "--remote",
        "-r",
        help="List projects on your GitHub.",
        show_default=False,
    ),
    all_: bool = typer.Option(
        False,
        "--all",
        "-a",
        help="List all projects, local and on your GitHub.",
        show_default=False,
    ),
) -> None:
    """
    Show your development projects.

    By default will only list the names of projects that exist locally
    in the configured "projects_dir" location.

    If "remote" is specified, the projects belonging to you on GitHub
    will be shown.

    If "all" is specified, all projects both local and remote will be shown
    separated by local and remote.

    Examples:

    $ pytoil project list

    $ pytoil project list --remote

    $ pytoil project list --all
    """

    # Everything below requires a valid config
    config = Config.get()
    config.raise_if_unset()

    # Should automatically fetch details from config
    api = API()

    # Shouldnt specify remote and all
    if remote and all_:
        raise typer.BadParameter("'--remote' and '--all' cannot be used together.")

    # Since local is default, iterdir is a generator, and list comps are fast
    # we can do this upfront with minimal cost
    # also someone is unlikely to have thousands of local project directories
    # that might slow this down
    local_projects: List[str] = sorted(
        [
            f.name
            for f in config.projects_dir.iterdir()
            if f.is_dir() and not f.name.startswith(".")
        ],
        key=str.casefold,  # casefold means sorting works independent of case
    )

    if remote or all_:
        # Only grab remotes if specifically requested
        # Avoid hitting the API if we don't have to
        remote_projects: List[str] = sorted(api.get_repo_names(), key=str.casefold)

        if remote:
            typer.secho("\nRemote Projects:\n", fg=typer.colors.BLUE, bold=True)
            for project in remote_projects:
                typer.echo(project)
        else:
            # Must be all
            # First show locals
            typer.secho("\nLocal Projects:\n", fg=typer.colors.BLUE, bold=True)
            for project in local_projects:
                typer.echo(project)

            # Now show remotes
            typer.secho("\nRemote Projects:\n", fg=typer.colors.BLUE, bold=True)
            for project in remote_projects:
                typer.echo(project)
    else:
        # Just locals as default
        typer.secho("\nLocal Projects:\n", fg=typer.colors.BLUE, bold=True)
        for project in local_projects:
            typer.echo(project)


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
    """

    # Everything below needs a valid config
    config = Config.get()
    config.raise_if_unset()

    # Set because we don't care about sorting or printing
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
