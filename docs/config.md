# Config

## Required

There's really not much to configure, all pytoil *needs* you to specify is:

* What your GitHub username is (`username`)
* Your GitHub personal access token (`token`)

If you don't know how to generate a GitHub token, check out the [docs].

## Optional

There are also some *optional* configurations you can tweak:

|        Key        |                                              Definition                                               |       Default       |
| :---------------: | :---------------------------------------------------------------------------------------------------: | :-----------------: |
|  `projects_dir`   |                                     Where you keep your projects                                      | `$HOME/Development` |
|     `vscode`      |                           Whether you want pytoil to open things in VSCode                            |        False        |
|     `code_bin`    |                           The name of the VSCode binary (code or code-insiders)                       |        `code`       |
| `common_packages` | List of packages you want pytoil to inject in every environment it creates (linters, formatters etc.) |       `None`        |
|   `init_on_new`   |        Whether you want pytoil to initialise an empty git repo when it makes a fresh project          |        True         |

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

No config file yet!
Making you a default one...
```

</div>

pytoil will then will write a default config state to a file: `~/.pytoil.yml`.

!!! note

    This command will only write a config file if it doesn't find one already. If one already exists, running `pytoil config show` will show you the settings from that file.

When you open the default config state you just wrote, it will look like this:

```yaml
# ~/.pytoil.yml

projects_dir: /Users/you/Development
token: This is your GitHub personal access token
username: This is your GitHub username
vscode: false
init_on_new: true
```

!!! warning

    `projects_dir` must be the **absolute** path to where you keep your projects. So you'll need to explicitly state the entire path (as in the example above) starting from the root.

You should now edit the config file to your liking. Your username and token are required for GitHub API access and will cause an error on most pytoil operations so these must be filled out. Everything else is optional :thumbsup:

So as an example, your filled out config file might look like this:

```yaml
# ~/.pytoil.yml

projects_dir: /Users/me/Projects
token: jbs822qbs982whbd97g # I've made this up
username: FollowTheProcess
vscode: true
common_packages:
  - black
  - flake8
  - mypy>=0.790
  - isort
init_on_new: true
```

!!! tip

    You can also interact with the pytoil config file via pytoil itself using the `pytoil config` command group.

[docs]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
[checkout]: ./commands/checkout.md
