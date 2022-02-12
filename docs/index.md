![logo](./img/logo.png)

[![License](https://img.shields.io/github/license/FollowTheProcess/pytoil)](https://github.com/FollowTheProcess/pytoil)
[![PyPI](https://img.shields.io/pypi/v/pytoil.svg?logo=python)](https://pypi.python.org/pypi/pytoil)
[![GitHub](https://img.shields.io/github/v/release/FollowTheProcess/pytoil?logo=github&sort=semver)](https://github.com/FollowTheProcess/pytoil)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/FollowTheProcess/pytoil)
[![CI](https://github.com/FollowTheProcess/pytoil/workflows/CI/badge.svg)](https://github.com/FollowTheProcess/pytoil/actions?query=workflow%3ACI)
[![codecov](https://codecov.io/gh/FollowTheProcess/pytoil/branch/main/graph/badge.svg?token=OLMR2P3J6N)](https://codecov.io/gh/FollowTheProcess/pytoil)
[![Downloads](https://static.pepy.tech/personalized-badge/pytoil?period=month&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads/month)](https://pepy.tech/project/pytoil)

> ***toil***
<br/>
> *"Long, strenuous or fatiguing labour"*

* **Source Code**: [https://github.com/FollowTheProcess/pytoil](https://github.com/FollowTheProcess/pytoil)

* **Documentation**: [https://FollowTheProcess.github.io/pytoil/](https://FollowTheProcess.github.io/pytoil/)

## What is it?

*pytoil is a small, helpful CLI to take the toil out of software development!*

`pytoil` is a handy tool that helps you stay on top of all your projects, remote or local. It's primarily aimed at python developers but you could easily use it to manage any project!

pytoil is:

* Easy to use ✅
* Easy to configure ✅
* Safe (it won't edit your repos at all) ✅
* Snappy (it's asynchronous from the ground up and as much as possible is done concurrently, clone all your repos in seconds!) 💨
* Useful! (I hope 😃)

Say goodbye to janky bash scripts 👋🏻

## Background

Like many developers I suspect, I quickly became bored of typing repeated commands to manage my projects, create virtual environments, install packages, fire off `cURL` snippets to check if I had a certain repo etc.

So I wrote some shell functions to do some of this for me...

And these shell functions grew and grew and grew.

Until one day I saw that the file I kept these functions in was over 1000 lines of bash (a lot of `printf`'s so it wasn't all logic but still). And 1000 lines of bash is *waaaay* too much!

And because I'd basically hacked it all together, it was **very** fragile. If a part of a function failed, it would just carry on and wreak havoc! I'd have to do `rm -rf all_my_projects`... I mean careful forensic investigation to fix it.

So I decided to make a robust CLI with the proper error handling and testability of python, and here it is! 🎉

## Installation

As pytoil is a CLI program, I'd recommend installing with [pipx].

<div class="termy">

```console
$ pipx install pytoil
---> 100%
Successfully installed pytoil
```

</div>

!!! note

    If you don't know what pipx is, go check it out! But basically it allows python CLI tools to be installed in their own sandboxed environments but you can still access the CLI as if it was installed globally!

You can always fall back to pip

<div class="termy">

```console
$ python3 -m pip install pytoil
---> 100%
Successfully installed pytoil
```

</div>

!!! warning

    keep in mind though, you'll have to install it globally for it to work so it might be better to use pipx

pytoil will install everything it needs *in python* to work. However, it's full feature set can only be accessed if you have the following external dependencies:

* [git]
* [conda] (if you work with conda environments)
* [VSCode] (if you want to use pytoil to automatically open your projects for you)
* [poetry] (if you want to create poetry environments)
* [flit] (if you want to create flit environments)

## Quickstart

`pytoil` is super easy to get started with.

After you install pytoil, the first time you run it you'll get something like this.

<div class="termy">

```console
$ pytoil <any command>

No pytoil config file detected!
? Interactively configure pytoil? [y/n]
```

</div>

If you say yes, pytoil will walk you through a few questions and fill out your config file with the values you enter. If you'd rather not do this interactively, just say no and it will instead put a default config file in the right place for you to edit later.

Once you've configured it properly, you can do things like...

#### See your local and remote projects

<div class="termy">

```console
$ pytoil show local
Local Projects

Showing 3 out of 3 local projects

  Name              Created          Modified
 ───────────────────────────────────────────────────
  project 1         13 days ago      9 days ago
  project 2         a day ago        a minute ago
  project 3         a month ago      a month ago
```

</div>

#### See which ones you have on GitHub, but not on your computer

<div class="termy">

```console
$ pytoil show diff
Diff: Remote - Local

Showing 3 out of 3 projects

  Name             Size       Created                Modified
 ─────────────────────────────────────────────────────────────────────────
  remote 1         154.6 kB   a month ago            29 days ago
  remote 2         2.1 MB     1 year, 15 days ago    11 months ago
  remote 3         753.7 kB   1 year, 6 months ago   a month ago
```

</div>

#### Easily grab a project, regardless of where it is

<div class="termy">

```console
$ pytoil checkout myproject

// Will now either open that project if local
// or clone it, then open it if not
```

</div>

#### Create a new project and virtual environment in one go

<div class="termy">

```console
$ pytoil new myproject --venv venv

Creating project: 'myproject' at '/Users/you/projects/myproject'

Creating virtual environment for: 'myproject'
```

</div>

#### And even do this from a [cookiecutter] template

<div class="termy">

```console
$ pytoil new myproject --venv venv --cookie https://github.com/some/cookie.git

Creating project: 'myproject' with cookiecutter template: 'https://github.com/some/cookie.git'

// You'll then be asked all the cookiecutter questions defined in the template
// After which pytoil will take over and create the virtual environment as normal
```

</div>

And loads more!

### Help

Like all good CLI programs, pytoil (as well as all it's subcommands, and all *their* subcommands!) has a `--help` option to show you what to do.

<div class="termy">

```console
$ pytoil --help

Usage: pytoil [OPTIONS] COMMAND [ARGS]...

  Helpful CLI to automate the development workflow.

  - Create and manage your local and remote projects

  - Build projects from cookiecutter templates.

  - Easily create/manage virtual environments.

  - Minimal configuration required.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  cache     Interact with pytoil's cache.
  checkout  Checkout an existing development project.
  config    Interact with pytoil's configuration.
  docs      Open pytoil's documentation in your browser.
  find      Quickly locate a project.
  gh        Open one of your projects on GitHub.
  info      Get useful info for a project.
  keep      Remove all but the specified projects.
  new       Create a new development project.
  pull      Pull down your remote projects.
  remove    Remove projects from your local filesystem.
  show      View your local/remote projects.
```

</div>

!!! info

    pytoil's CLI is designed such that if you don't specify any arguments, it won't do anything! just show you the `--help`. This is called being a 'well behaved' unix command line tool.

    This is true for any subcommand of pytoil so you won't accidentally break anything if you don't specify arguments :tada:.

And if you get truly stuck, you can quickly open pytoil's documentation with:

<div class="termy">

```console
$ pytoil docs

Opening pytoil's documentation in your browser...

// Now you'll be on this page in whatever your default browser is!
```

</div>

[git]: https://git-scm.com
[conda]: https://docs.conda.io/en/latest/
[VSCode]: https://code.visualstudio.com
[config]: config.md
[pipx]: https://pipxproject.github.io/pipx/
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[poetry]: https://python-poetry.org
[flit]: https://flit.readthedocs.io
