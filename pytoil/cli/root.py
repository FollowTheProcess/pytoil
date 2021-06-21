"""
The pytoil app CLI command and it's direct child commands.

Author: Tom Fleet
Created: 18/06/2021
"""


from enum import Enum
from typing import List

import httpx
import typer
from wasabi import msg

from pytoil import __version__
from pytoil.api import API
from pytoil.cli import config, pull, remove, show, utils
from pytoil.config import Config
from pytoil.exceptions import EnvironmentAlreadyExistsError, RepoNotFoundError
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.vscode import VSCode

PYTOIL_DOCS_URL: str = "https://followtheprocess.github.io/pytoil/"

# Create the root app
app = typer.Typer(name="pytoil", no_args_is_help=True)

# Add the sub commands
app.add_typer(show.app, name="show")
app.add_typer(remove.app, name="remove")
app.add_typer(config.app, name="config")
app.add_typer(pull.app, name="pull")


# Choice of virtual environments for a new project
class VirtualEnv(str, Enum):
    """
    Choice of virtualenvs to create in a new project.
    """

    venv = "venv"
    conda = "conda"
    none = "none"


def version_callback(value: bool) -> None:
    if value:
        typer.echo(f"pytoil version: {__version__}")
        raise typer.Exit(0)


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
def checkout(
    project: str = typer.Argument(
        ...,
        help="Name of the project to checkout.",
    ),
    venv: bool = typer.Option(
        False,
        "--venv",
        "-v",
        help="Attempt to auto-create a virtual environment.",
        show_default=False,
    ),
) -> None:
    """
    Checkout an existing development project.

    The checkout command lets you easily resume work on an existing project,
    whether that project is available locally in your configured projects
    directory, or if it is on GitHub.

    If pytoil finds your project locally, and you have enabled VSCode in your
    config file it will open it for you. If not, it will just tell you it already
    exists locally and where to find it.

    If your project is on GitHub, pytoil will clone it for you and then open it
    (or tell you where it cloned it if you dont have VSCode set up).

    Finally, if checkout can't find a match after searching locally and on GitHub,
    it will prompt you to use 'pytoil new' to create a new one.

    You can also ask pytoil to automatically create a virtual environment on
    checkout with the '--venv/-v' flag. This only happens for projects pulled down
    from GitHub to avoid accidentally screwing up local projects.

    If the '--venv/-v' flag is used, pytoil will look at your project to try and detect
    which type of environment to create (conda or standard python).

    More info can be found in the documentation.

    Examples:

    $ pytoil checkout my_project

    $ pytoil checkout my_project --venv
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    # Setup the objects required
    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )
    code = VSCode(root=repo.local_path)
    git = Git()

    is_local = repo.exists_local()
    try:
        is_remote = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        if is_local:
            # No environment or git stuff here, chances are if it exists locally
            # user has already done all this stuff
            msg.info(f"{repo.name!r} available locally.", spaced=True)

            if config.vscode:
                msg.text(f"Opening {repo.name!r} in VSCode.")
                code.open()

        elif is_remote:
            msg.info(f"{repo.name!r} found on GitHub. Cloning...", spaced=True)
            git.clone(url=repo.clone_url, check=True, cwd=config.projects_dir)

            env = repo.dispatch_env()

            if venv:
                if not env:
                    msg.warn(
                        "Unable to auto-detect required environent. Skipping.",
                        spaced=True,
                    )
                else:
                    msg.info("Auto creating correct virtual environment.", spaced=True)

                    try:
                        with msg.loading("Creating Environment..."):
                            env.create(packages=config.common_packages)
                    except EnvironmentAlreadyExistsError:
                        msg.warn(
                            title="Environment already exists!",
                            text="No need to create a new one. Skipping.",
                        )
                    finally:
                        if config.vscode:
                            code.set_python_path(python_path=env.executable)

            if config.vscode:
                msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
                code.open()

        else:
            msg.warn(
                title=f"{repo.name!r} not found locally or on GitHub!",
                text=f"Does it exist? If not, create a new project with 'pytoil new {repo.name}'.",  # noqa: E501
                exits=1,
            )


@app.command(context_settings={"allow_extra_args": True})
def new(
    ctx: typer.Context,
    project: str = typer.Argument(..., help="Name of the project to create."),
    cookie: str = typer.Option(
        None,
        "--cookie",
        "-c",
        help="URL to a cookiecutter template repo from which to build the project.",
    ),
    venv: VirtualEnv = typer.Option(
        VirtualEnv.none,
        "--venv",
        "-v",
        help="Which type of virtual environment to create for the project.",
        case_sensitive=False,
        show_default=True,
    ),
    no_git: bool = typer.Option(
        False,
        "--no-git",
        "-n",
        help="Don't initialise an empty git repo in the app of the project.",
    ),
) -> None:
    """
    Create a new development project.

    Bare usage will simply create an empty folder in your configured projects
    directory.

    You can also create a project from a cookiecutter template by passing a valid
    url to the '--cookie/-c' flag.

    By default, pytoil will initialise an empty git repo in the folder, following
    the style of modern language build tools such as rust's cargo. You can disable
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
    """
    # Get config and ensure user can access API
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    # Setup the objects required
    api = API(username=config.username, token=config.token)
    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )
    code = VSCode(root=repo.local_path)
    git = Git()

    if ctx.args:
        packages: List[str] = config.common_packages + ctx.args
    else:
        packages = config.common_packages

    # Resolve config vs flag for no-git
    # flag takes priority over config
    use_git: bool = config.init_on_new and not no_git

    # Check is project already exists and warn/exit if so
    utils.pre_new_checks(repo=repo, api=api)

    # If we get here, all is well and we can create stuff!
    utils.make_new_project(
        repo=repo, git=git, cookie=cookie, use_git=use_git, config=config
    )

    if venv.value == venv.venv:
        env = utils.create_virtualenv(repo=repo, packages=packages)

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.set_python_path(env.executable)
            code.open()

    elif venv.value == venv.conda:
        env = utils.create_condaenv(repo=repo, packages=packages)

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.set_python_path(env.executable)
            code.open()

    else:
        # Only other allowed condition is none
        typer.secho(
            "Virtual environment not requested. Skipping environment creation.",
            fg=typer.colors.YELLOW,
        )

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.open()


@app.command()
def info(
    project: str = typer.Argument(..., help="Name of the project to fetch info for.")
) -> None:
    """
    Get useful info for a project.

    Given a project name (can be local or remote), 'info' will return a summary
    description of the project.

    If the project is on GitHub, info will prefer getting information from the GitHub
    API as this is more detailed.

    If the project is local only, some information is extracted from the operating
    system about the project.

    Examples:

    $ pytoil info my_project
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )

    try:
        _ = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)

    try:
        with msg.loading(f"Fetching info for {project!r}..."):
            info_dict = repo.info(api=api)

    except RepoNotFoundError:
        msg.warn(
            f"{project!r} not found locally or on GitHub. Was it a typo?",
            spaced=True,
            exits=1,
        )
    else:
        typer.secho(f"\nInfo for {project!r}:\n", fg=typer.colors.CYAN, bold=True)
        for key, val in info_dict.items():
            typer.echo(f"{key}: {val}")


@app.command()
def docs() -> None:  # pragma: no cover
    """
    Open pytoil's documentation in your browser.

    Examples:

    $ pytoil docs
    """
    msg.info("Opening pytoil's docs in your browser...", spaced=True)
    typer.launch(url=PYTOIL_DOCS_URL)


@app.command()
def gh(
    project: str = typer.Argument(..., help="Name of the project to go to on GitHub.")
) -> None:  # pragma: no cover
    """
    Open one of your projects on GitHub.

    Given a project name (must exist on GitHub and be owned by you),
    'gh' will open your browser and navigate to the project on GitHub.

    Examples:

    $ pytoil gh my_project
    """
    config = Config.from_file()
    utils.warn_if_no_api_creds(config)

    api = API(username=config.username, token=config.token)

    repo = Repo(
        owner=config.username,
        name=project,
        local_path=config.projects_dir.joinpath(project),
    )

    try:
        exists_remote = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        if not exists_remote:
            msg.warn(
                f"{project!r} not found on GitHub! Was it a typo?", spaced=True, exits=1
            )
        else:
            msg.info(f"Opening {project!r} on GitHub...", spaced=True)
            typer.launch(url=repo.html_url)
