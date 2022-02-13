# Config

The `config` subcommand is pytoil's programmatic access to it's own configuration file! Here you can get, show and get help about the configuration.

## Help

<div class="termy">

```console
$ pytoil config --help

Usage: pytoil config [OPTIONS] COMMAND [ARGS]...

  Interact with pytoil's configuration.

  The config command group allows you to get, show and explain pytoil's
  configuration.

Options:
  --help  Show this message and exit.

Commands:
  edit     Open pytoil's config file in $EDITOR.
  explain  Print a list and description of pytoil config values.
  get      Get the currently set value for a config key.
  show     Show pytoil's config.
```

</div>

## Get

`get` does what it says. It gets a valid config key-value pair from your file and shows it to you. Simple!

<div class="termy">

```console
$ pytoil config get vscode

vscode: True
```

</div>

## Show

`show` is just a handy way of seeing what the current config is without having to go to the config file!

<div class="termy">

```console
$ pytoil config show

               Key   Value
 ─────────────────────────────────────────────────────────────
     projects_dir:   /Users/tomfleet/Development
            token:   lknskjb983e7g23hb8
         username:   FollowTheProcess
           vscode:   True
         code_bin:   code-insiders
        conda_bin:   mamba
  common_packages:   ['black', 'mypy', 'isort', 'flake8']
    cache_timeout:   120
              git:   True
```

</div>

## Edit

`edit` simply opens up the pytoil config file in your $EDITOR so you can make any changes you like!

<div class="termy">

```console
$pytoil config edit

Opening ~/.pytoil.toml in your $EDITOR
```

</div>

## Explain

The command `pytoil config explain` outputs a (hopefully) helpful description of the pytoil configuration schema.

<div class="termy">

```console
$ pytoil config explain

======================= The '.pytoil.yml' config file =======================


- projects_dir (bool)

    The absolute path to where you keep your development projects
    (e.g. /Users/you/Projects)

- token (str)

    Your GitHub personal access token. This must have a minimum of repo
    read access. See the documentation here:
    https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure/creating-a-personal-access-token

    Pytoil will try and get this from the config file initially, then fall back to the $GITHUB_TOKEN environment
    variable. If neither of these places are set, you will not be able to use pytoil commands that rely on the
    GitHub API. Pytoil will notify you of this when any of these commands are called.

- username (str)

    Your GitHub username.

- vscode (bool)

    Whether you want pytoil to open projects up using VSCode. This will happen on 'new' and 'checkout'.

- code_bin (str)

    The name of the VSCode binary ('code' or 'code-insiders')

- conda_bin (str)

    The name of the conda binary ('conda' or 'mamba')

- common_packages (List[str])

    A list of python package names to inject into every virtual environment pytoil creates
    (e.g. linters, formatters and other dev dependencies).

- cache_timeout (int)

    The number of seconds pytoil keeps a cache of GitHub API requests for. Subsequent API calls
    within this window will be served from cache not from the API.

- git (bool)

    Whether or not you want pytoil to create an empty git repo when you make a new project with
    'pytoil new'. This can also be disabled on a per use basis using the '--no-git' flag.
```

</div>

[pydantic]: https://pydantic-docs.helpmanual.io
