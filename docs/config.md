# Config

## Required

There's really not much to configure, all pytoil *needs* you to specify is:

* What your GitHub username is (`username`)
* Your GitHub personal access token (`token`)

If you don't know how to generate a GitHub token, check out the [docs].

!!! note

    If you don't specify `token` but have `GITHUB_TOKEN` set as environment variable, pytoil will use that instead :thumbsup:

## Optional

There are also some *optional* configurations you can tweak:

|        Key        |                                              Definition                                               |       Default       |
| :---------------: | :---------------------------------------------------------------------------------------------------: | :-----------------: |
|  `projects_dir`   |                                     Where you keep your projects                                      | `$HOME/Development` |
|     `vscode`      |                           Whether you want pytoil to open things in VSCode                            |        False        |
|     `code_bin`    |                           The name of the VSCode binary (code or code-insiders)                       |        `code`       |
|     `conda_bin`   |                           The name of the conda binary (conda or mamba)                               |        `conda`      |
| `common_packages` | List of packages you want pytoil to inject in every environment it creates (linters, formatters etc.) |       `None`        |
| `cache_timeout`   | Maximum duration you want pytoil to keep a cache of API responses for (seconds)                       |       120           |
|   `git`           |        Whether you want pytoil to initialise and commit a git repo when it makes a fresh project      |        True         |

These optional settings don't have to be set if you're happy using the default settings!

!!! info

    Don't worry about giving pytoil your personal token. All we do with it is make HTTP GET and POST requests to the GitHub
    API using your token to authenticate the requests. This is essential to pytoil's functionality and it lets us:

    * See your repos and get some basic info about them (name, date created etc.)
    * Create forks of other people's projects when requested (e.g. when using [checkout])

    In fact, the only permissions pytoil needs is repo and user access! :smiley:

!!! note

    I used VSCode as the only configurable editor as it's the one I use and is therefore the only one I have experience with configuring programmatically and launching via the command line.

    If you want to help add support for more editors then PR's are always welcome!

## The Config File

After you install pytoil, the first time you run it you'll get something like this.

<div class="termy">

```console
$ pytoil

No pytoil config file detected!
? Interactively configure pytoil? [y/n]
```

</div>

If you say yes, pytoil will walk you through a few questions and fill out your config file with the values you enter. If you'd rather not do this interactively, just say no and it will instead put a default config file in the right place for you to edit later.

!!! note

    This command will only write a config file if it doesn't find one already. If one already exists, running `pytoil config show` will show you the settings from that file. Remember, you can always quickly edit your pytoil config file using `pytoil config edit` 🔥

When you open the config file, it will look something like this:

```toml
# ~/.pytoil.toml

[pytoil]
cache_timeout = 120
code_bin = "code"
conda_bin = "conda"
common_packages = []
git = true
projects_dir = "/Users/you/Development"
token = "Your GitHub personal access token"
username = "Your GitHub username"
vscode = false
```

!!! warning

    `projects_dir` must be the **absolute** path to where you keep your projects. So you'll need to explicitly state the entire path (as in the example above) starting from the root.

You should now edit the config file to your liking. Your username and token are required for GitHub API access and will cause an error on most pytoil operations so these must be filled out. Everything else is optional :thumbsup:

So as an example, your filled out config file might look like this:

```toml
# ~/.pytoil.toml

[pytoil]
cache_timeout = 500
code_bin = "code"
conda_bin = "mamba"
common_packages = ["black", "mypy", "isort", "flake8"]
git = true
projects_dir = "/Users/you/Development"
token = "asljas98ghefiub29e8b" # I've made this up
username = "FollowTheProcess"
vscode = true

```

!!! tip

    You can also interact with the pytoil config file via pytoil itself using the `pytoil config` command group.

[docs]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
[checkout]: ./commands/checkout.md
