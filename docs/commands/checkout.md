# Checkout

`checkout` (not to be confused with `git checkout`) allows to easily resume work on an ongoing development project.

## Help

<div class="termy">

```console
$ pytoil checkout --help

Usage: pytoil checkout [OPTIONS] PROJECT

  Checkout an existing development project.

  The checkout command lets you easily resume work on an existing project,
  whether that project is available locally in your configured projects
  directory, or if it is on GitHub.

  If pytoil finds your project locally, and you have specified an editor in
  your config file it will open it for you. If not, it will just tell you it
  already exists locally and where to find it.

  If your project is on your GitHub, pytoil will clone it for you and then
  open it (or tell you where it cloned it if you dont have an editor set up).

  Finally, if checkout can't find a match after searching locally and on
  GitHub, it will prompt you to use 'pytoil new' to create a new one.

  If you pass the shorthand to someone elses repo e.g. 'someoneelse/repo'
  pytoil will detect this and ask you whether you want to create a fork or
  clone the original. Forking happens asynchronously so we give it a few
  seconds, then check whether or not your fork exists yet. If it does, all is
  well and we can clone it for you automatically. If not, (which is totally
  normal), we'll let you know. In which case just give it a few seconds then a
  'pytoil checkout repo' will bring it down as normal.

  If you pick "clone" then it just clones the original for you.

  You can also ask pytoil to automatically create a virtual environment on
  checkout with the '--venv/-v' flag. This only happens for projects pulled
  down from GitHub to avoid accidentally screwing up local projects.

  If the '--venv/-v' flag is used, pytoil will look at your project to try and
  detect which type of environment to create e.g. conda, flit, poetry,
  standard python etc.

  The '--venv/-v' flag will also attempt to detect if the project you're
  checking out is a python package, in which case it will install it's
  requirements into the created environment.

  More info about this can be found in the documentation. Use `pytoil docs` to
  go there.

  Examples:

  $ pytoil checkout my_project

  $ pytoil checkout my_project --venv

  $ pytoil checkout someoneelse/project

Options:
  -v, --venv  Attempt to auto-create a virtual environment.
  --help      Show this message and exit.
```

</div>

## Local Project

If the project is available locally, `checkout` will simply open it for you using whatever editor you have configured pytoil to use

<div class="termy">

```console
// Some project that's already local
$ pytoil checkout my_local_project

Project: 'my_local_project' found locally!

Opening 'my_github_project' with <editor>...
```

</div>

## Remote Project

If pytoil can't find your project locally, but it is on your GitHub `checkout` will:

* Clone it to your projects directory
* Open it for you (if you configure an appropriate editor in [config])

<div class="termy">

```console
// Some project that's on GitHub
$ pytoil checkout my_github_project

Project: 'my_github_project' found on GitHub! Cloning...
// You might see some git clone output here

Opening 'my_github_project' with <editor>...
```

</div>

!!! info "What's an appropriate editor?"

    Initially pytoil only supported VSCode as that was what I was most familiar with. However since version 0.28.0, pytoil now supports specifying an editor
    using the `editor` key in the config file.

    However, there are a few caveats:

    * The editor must be "directory aware" i.e. it must be able to open entire directories at once e.g. VSCode, Pycharm, Atom, Sublime etc.
    * It must have a command line interface, the name of which you should use when setting the `editor` config key, e.g. `code` or `code-insiders` for VSCode
    * The command to launch the editor at a certain filepath must be of the form `<cmd> <path>`

    If your editor ticks all those boxes, you can use it with pytoil 👍🏻

## Someone else's project

A common workflow in open source is to fork someone elses project and then work on your fork. With `pytoil` this can be done in the same command! If you provide the shorthand repo path to `pytoil checkout` e.g. `someoneelse/repo`, `pytoil` will:

* Ask you whether you want to fork it and clone your fork, or just clone the original
* If you pick fork it will fork the project to your GitHub, clone it for you and add the original repo as remote "upstream"
* If you pick clone it will simply clone the original repo for you e.g. if you're a collaborator and want to checkout a PR

Basically all the chores you would have to do to work on a open source project! :tada:

<div class="termy">

```console
// Someone else's project
$ pytoil checkout someone/their_github_project

'someone/their_github_project' belongs to 'someone'
? Fork project or clone the original?
> fork
> clone

Do awesome stuff!
```

</div>

!!! note

    Forking happens asynchronously on GitHub's end and there is no guarantee on a timeline (although GitHub is very well engineered and this normally happens pretty much straight away) so we make a best effort here to wait for GitHub's internal state to synchronise and check if the fork was a success. However, this can sometimes time out, in which case pytoil will let you know and handle this gracefully :thumbsup:

    If this happens to you, all you need to do is wait a few seconds and then try `pytoil checkout <project>` again.

## Automatically Create a Virtual Environment

If you pass the `--venv` option, `checkout` will also:

* Try to detect what environment would work best for the project (conda, venv, flit, poetry)
* Auto create this virtual environment
* Look for requirements files that specify dependencies such as `environment.yml` for conda, `setup.cfg` or `setup.py` for normal python packages etc.

<div class="termy">

```console
// Some project that's on GitHub
$ pytoil checkout my_github_project --venv

Project: 'my_github_project' found on GitHub! Cloning...
// You might see some git clone output here

Auto-creating correct virtual environment
// Here you might see some conda or venv stuff

Opening 'my_github_project' with <editor>...
```

</div>

!!! note

    pytoil looks for certain files in your project (like `setup.py`, `setup.cfg`, `pyproject.toml`, `environment.yml` etc.) and that's how it decides which environment to create. If it isn't totally sure what environment to create, it will just skip this step and let you know!

### How pytoil Knows What to Install

The `--venv` implementation is quite complex (and it took me a while to get it right!) but effectively, `pytoil` will look at the contents of your cloned project to decide what to do, create the matching virtual environment, then delegate to the appropriate tool to install dependencies.

A summary of what `pytoil` does when it finds certain files is found below, the search priority is in the same order as presented and `pytoil` will match on the first found condition to create the environment:

### `environment.yml`

Must mean it's a conda project, delegate to conda using `conda env create --file environment.yml`

### `requirements.txt` or `requirements-dev.txt`

Python script or non-package project e.g. django web app, delegate to pip using `pip install -r <file>`

Prefers `requirements-dev.txt` if present as it will have everything needed to work on the project, falls back to `requirements.txt` if not.

### `setup.cfg` or `setup.py`

Python package, again delegate to pip using `pip install -e .[dev]`

Defaults to using the [dev] target for convention and to ensure the entire dev environment is set up, if this isn't present pip automatically falls back to `pip install -e .`

### `pyproject.toml` specifying poetry as a build tool

Python package managed with [poetry], here we basically delegate everything to poetry as it handles both the virtual environment and installation of dependencies.

`pytoil` is effectively doing `poetry install` as you might yourself.

### `pyproject.toml` specifying flit as a build tool

Python package managed with [flit], here we create a virtual environment the normal python way, then delegate to flit to install dependencies.

Something like `flit install` called from the directory of the project. (We actually do a bit more than this to make sure it only targets your local environment for that project, but that's the gist of it!)

### Else

If we get here, `pytoil` gives up and will tell you something along the lines of "could not detect correct virtual environment. skipping". Your project will still be checked out, but you'll have to do the virtual environment stuff yourself I'm afraid! :pensive: But we gave it our best shot!

!!! note

    Although we've tried to make the implementation of this as robust as possible, it's quite complex and there's bound to be edge cases lurking here somewhere. If you hit any, please file an issue and maybe even try and fix it yourself and throw us a PR :tada:

    Remember if you need more custom behaviour than this, you can just plain `pytoil checkout` without the `--venv` and `pytoil` won't try and be clever, it will just straight up clone the project for you to do whatever you want with!

[config]: ../config.md
[poetry]: https://python-poetry.org
[flit]: https://flit.readthedocs.io/en/latest/
