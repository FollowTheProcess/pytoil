"""
The pytoil new command.

Author: Tom Fleet
Created: 25/06/2021
"""

from typing import List

import httpx
import typer
from cookiecutter.main import cookiecutter
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.environments import Conda, Environment, Venv, VirtualEnv
from pytoil.exceptions import (
    CargoNotInstalledError,
    EnvironmentAlreadyExistsError,
    GoNotInstalledError,
)
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.starters import GoStarter, PythonStarter, RustStarter, Starter
from pytoil.vscode import VSCode

app = typer.Typer()


@app.command(context_settings={"allow_extra_args": True})
def new(
    ctx: typer.Context,
    project: str = typer.Argument(
        ...,
        help="Name of the project to create.",
    ),
    cookie: str = typer.Option(
        None,
        "--cookie",
        "-c",
        help="URL to a cookiecutter template repo from which to build the project.",
    ),
    starter: Starter = typer.Option(
        Starter.none,
        "--starter",
        "-s",
        help="Use a language-specific starter template",
        case_sensitive=False,
        show_default=True,
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

    If you just want a very simple, language-specific starting template, use the
    '--starter/-s' option.

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

    $ pytoil new my_project --starter python
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
    pre_new_checks(repo=repo, api=api)

    # Cant use --venv with non-python starters
    if (
        starter.value != starter.none  # User specified starter
        and starter.value != starter.python  # The starter is not python
        and venv.value != venv.none  # And the user wants a virtual environment
    ):
        msg.warn(
            f"Can't create a venv for {starter.value} project!",
            spaced=True,
            exits=1,
        )

    # If we get here, all is well and we can create stuff!
    make_new_project(
        repo=repo,
        git=git,
        cookie=cookie,
        starter=starter,
        use_git=use_git,
        config=config,
    )

    if venv.value == venv.venv:
        env = create_virtualenv(repo=repo, packages=packages)

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.set_workspace_python(env.executable)
            code.open()

    elif venv.value == venv.conda:
        env = create_condaenv(repo=repo, packages=packages)

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.set_workspace_python(env.executable)
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


def make_new_project(
    repo: Repo, git: Git, cookie: str, starter: Starter, use_git: bool, config: Config
) -> None:
    """
    Create a new development project either from a cookiecutter
    template or from scratch.
    """
    # Can't use starter and cookiecutter at the same time
    if starter.value != Starter.none and cookie:
        msg.warn(
            "'--cookie' and '--starter' are mutually exclusive.",
            exits=1,
        )

    if cookie:
        # We don't initialise a git repo for cookiecutters
        # some templates have hooks which do this, mine do!
        msg.info(f"Creating {repo.name!r} from cookiecutter: {cookie!r}.")
        cookiecutter(template=cookie, output_dir=config.projects_dir)

    elif starter == Starter.go:
        msg.info(f"Creating {repo.name!r} from starter: {starter.value!r}.")
        go_st = GoStarter(path=config.projects_dir, name=repo.name)

        try:
            go_st.generate(username=config.username)
        except GoNotInstalledError:
            msg.fail("Error: Go not installed.", spaced=True, exits=1)

        if use_git:
            git.init(path=repo.local_path, check=True)

    elif starter == Starter.python:
        msg.info(f"Creating {repo.name!r} from starter: {starter.value!r}.")
        py_st = PythonStarter(path=config.projects_dir, name=repo.name)
        py_st.generate()

        if use_git:
            git.init(path=repo.local_path, check=True)

    elif starter == Starter.rust:
        msg.info(f"Creating {repo.name!r} from starter: {starter.value!r}.")
        rs_st = RustStarter(path=config.projects_dir, name=repo.name)

        try:
            rs_st.generate()
        except CargoNotInstalledError:
            msg.fail("Error: Cargo not installed.", spaced=True, exits=1)

    else:
        msg.info(f"Creating {repo.name!r} at {repo.local_path}.")
        # Make an empty dir and git repo
        repo.local_path.mkdir(parents=True)

        if use_git:
            git.init(path=repo.local_path, check=True)


def pre_new_checks(repo: Repo, api: API) -> None:
    """
    Checks whether the repo already exists either locally
    or remotely, prints helpful warning messages and exits
    the program if True.
    """

    is_local = repo.exists_local()

    try:
        is_remote = repo.exists_remote(api=api)
    except httpx.HTTPStatusError as err:
        utils.handle_http_status_errors(error=err)
    else:

        if is_local:
            msg.warn(
                title=f"{repo.name!r} already exists locally!",
                text=f"To checkout this project, use 'pytoil checkout {repo.name}'.",
                spaced=True,
                exits=1,
            )
        elif is_remote:
            msg.warn(
                title=f"{repo.name!r} already exists on GitHub!",
                text=f"To checkout this project, use 'pytoil checkout {repo.name}'.",
                spaced=True,
                exits=1,
            )


def create_virtualenv(repo: Repo, packages: List[str]) -> Environment:
    """
    Creates and returns new virtual environment with packages and reports
    to user.
    """

    msg.info(
        f"Creating virtual environment for {repo.name!r}",
        text=f"Including packages: {', '.join(packages)}",
        spaced=True,
    )
    env = Venv(project_path=repo.local_path)
    with msg.loading("Working..."):
        env.create(packages=packages)

    return env


def create_condaenv(repo: Repo, packages: List[str]) -> Environment:
    """
    Creates and returns new conda environment with packages and reports
    to user.
    """
    msg.info(
        f"Creating conda environment for {repo.name!r}",
        text=f"Including packages: {', '.join(packages)}",
        spaced=True,
    )
    env = Conda(name=repo.name, project_path=repo.local_path)
    try:
        with msg.loading("Working..."):
            env.create(packages=packages)
    except EnvironmentAlreadyExistsError:
        msg.warn(
            f"Conda environment {env.name!r} already exists!", spaced=True, exits=1
        )

    return env
