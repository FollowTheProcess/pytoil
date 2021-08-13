# Config

The `config` subcommand is pytoil's programmatic access to it's own configuration file! Here you can get, set, show and get help about the configuration.

## Help

<div class="termy">

```console
$ pytoil config --help

Usage: pytoil config [OPTIONS] COMMAND [ARGS]...

  Interact with pytoil's configuration.

  The config command group allows you to get, set, and show pytoil's
  configuration. Getting and showing obviously do not edit the config file
  ($HOME/.pytoil.yml).

  Setting a key value pair using the 'config set' subcommand will cause the
  config file to be updated and overwritten. You will be prompted to confirm
  this however.

  Currently the only config key you cannot set on the command line is
  'common_packages'. If you want to change this, you'll have to do so in the
  config file itself.

Options:
  --help  Show this message and exit.

Commands:
  get   Get the currently set value for a config key.
  help  Print a list and description of pytoil config keys.
  set   Set a config key, value pair.
  show  Show pytoil's config.

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

## Set

`set` allows you to set a config key-value pair from the command line. This change will be saved to the config file, overwriting it, but only if you agree to the confirmation!

<div class="termy">

```console
$ pytoil config set projects_dir /Users/me/somewhereelse

This will set 'projects_dir' to /Users/me/somewhereelse. Are you sure? [y/N]: y

Config changed successfully!

'projects_dir' is now /Users/me/somewhereelse

```

</div>

!!! tip

    You can again use the `--force/-f` flag here if you want to override the confirmation :thumbsup:

!!! note

    Pytoil uses [pydantic] under the hood to ensure the types of the values (e.g. bool, str, pathlib.Path etc.) are all handled properly so you basically can't go wrong!

!!! warning

    The only config key you can't currently set via the command line is `common_packages`. This is to do with the way shells and CLI apps handle lists and I don't see an easy way to solve it!

    If you want to change this config setting, you will have to do it in the config file itself unfortunately :unamused:

    Luckily, this tends to be a "fire and forget" setting, typically used for linters and formatters common to all python projects so you won't have to change it much!

## Show

`show` is just a handy way of seeing what the current config is without having to go to the config file!

<div class="termy">

```console
$ pytoil config show

Pytoil Config:

projects_dir: '/Users/you/Development'
token: 'ljnbasbasbisyvo8'
username: 'FollowTheProcess'
vscode: True
common_packages: ['black', 'mypy', 'isort', 'flake8']
init_on_new: True

```

</div>

## Help (The other help)

This help (`pytoil config help` not `pytoil config --help`) outputs a (hopefully) helpful description of the pytoil configuration schema.

<div class="termy">

```console
$ pytoil config help

======================= The '.pytoil.yml' config file =======================


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

- common_packages (List[str])

    A list of python package names to inject into every virtual environment pytoil creates
    (e.g. linters, formatters and other dev dependencies).

- init_on_new (bool)

    Whether or not you want pytoil to create an empty git repo when you make a new project with
    'pytoil new'. This can also be disabled on a per use basis using the '--no-git' flag.

```

</div>

[pydantic]: https://pydantic-docs.helpmanual.io
