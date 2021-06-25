"""
The pytoil new command.

Author: Tom Fleet
Created: 25/06/2021
"""

from typing import List

import typer
from wasabi import msg

from pytoil.api import API
from pytoil.cli import utils
from pytoil.config import Config
from pytoil.environments import VirtualEnv
from pytoil.git import Git
from pytoil.repo import Repo
from pytoil.starters import Starter
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
    utils.pre_new_checks(repo=repo, api=api)

    # If we get here, all is well and we can create stuff!
    utils.make_new_project(
        repo=repo,
        git=git,
        cookie=cookie,
        starter=starter.value,
        use_git=use_git,
        config=config,
    )

    if venv.value == venv.venv:
        env = utils.create_virtualenv(repo=repo, packages=packages)

        if config.vscode:
            msg.info(f"Opening {repo.name!r} in VSCode.", spaced=True)
            code.set_workspace_python(env.executable)
            code.open()

    elif venv.value == venv.conda:
        env = utils.create_condaenv(repo=repo, packages=packages)

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
