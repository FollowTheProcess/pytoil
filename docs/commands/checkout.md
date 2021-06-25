# Checkout

`checkout` (not to be confused with `git checkout`) allows to easily resume work on an ongoing development project.

## Help

<div class="termy">

```console
// Some project thats already local
$ pytoil checkout --help

Usage: pytoil checkout [OPTIONS] PROJECT

  Checkout an existing development project.

  The checkout command lets you easily resume work on an existing project,
  whether that project is available locally in your configured projects
  directory, or if it is on GitHub.

  If pytoil finds your project locally, and you have enabled VSCode in your
  config file it will open it for you. If not, it will just tell you it
  already exists locally and where to find it.

  If your project is on GitHub, pytoil will clone it for you and then open
  it (or tell you where it cloned it if you dont have VSCode set up).

  Finally, if checkout can't find a match after searching locally and on
  GitHub, it will prompt you to use 'pytoil new' to create a new one.

  You can also ask pytoil to automatically create a virtual environment on
  checkout with the '--venv/-v' flag. This only happens for projects pulled
  down from GitHub to avoid accidentally screwing up local projects.

  If the '--venv/-v' flag is used, pytoil will look at your project to try
  and detect which type of environment to create (conda or standard python).

  More info can be found in the documentation.

  Examples:

  $ pytoil checkout my_project

  $ pytoil checkout my_project --venv

Arguments:
  PROJECT  Name of the project to checkout.  [required]

Options:
  -v, --venv  Attempt to auto-create a virtual environment.
  --help      Show this message and exit.

```

</div>

## Local Project

If the project is available locally, `checkout` will simply open it for you

<div class="termy">

```console
// Some project thats already local
$ pytoil checkout my_local_project

Project: 'my_local_project' found locally!

Opening 'my_github_project' in VSCode...
```

</div>

## Remote Project

If pytoil can't find your project locally, `checkout` will:

* Clone it to your projects directory
* Open it for you (if you configure VSCode in [config])

<div class="termy">

```console
// Some project thats on GitHub
$ pytoil checkout my_github_project

Project: 'my_github_project' found on GitHub! Cloning...
// You might see some git clone output here

Opening 'my_github_project' in VSCode...
```

</div>

!!! info "Why just VSCode?"

    When developing pytoil I was debating how to handle this. I use VSCode for everything but I know other people have different editor preferences. Initially I looked at using the `$EDITOR` environment variable but working out how best to launch a variety of possible editors from a CLI was tricky. Plus pytoil does things like alter workspace settings to point at the right virtual environment, and I only know how to do this with VSCode.

    PR's are very welcome though if you think you can introduce support for your preferred editor! :grin:

## Automatically Create a Virtual Environment

If you pass the `--venv` option, `checkout` will also:

* Try to detect what environment would work best for the project (conda or virtualenv)
* Auto create this virtual environment and install any configured common packages
* If you have VSCode configured, `pytoil` will also set your workspace `python.defaultInterpreterPath`

!!! note

    From about version 1.57.1, VSCode have been deprecating the workspace setting `python.pythonPath` in favour of `python.defaultInterpreterPath` which up until v0.6.0, pytoil used as part of the whole "automate your dev life" thing! These settings do differ in their functionality, which you can read about here: https://github.com/microsoft/vscode-python/issues/12313.

    But it turns out that because the only time we set this is when creating brand new projects, or checking out remote projects, these settings behave exactly the same for us, so it effectively represents a straight swap.

<div class="termy">

```console
// Some project thats on GitHub
$ pytoil checkout my_github_project --venv

Project: 'my_github_project' found on GitHub! Cloning...
// You might see some git clone output here

Auto-creating correct virtual environment
// Here you might see some conda or venv stuff

Opening 'my_github_project' in VSCode...
```

</div>

!!! note

    pytoil looks for certain files in your project (like `setup.py`, `setup.cfg`, `environment.yml` etc.) and that's how it decides which environment to create. If it isn't totally sure what environment to create, it will just skip this step and let you know!

[config]: ../config.md
