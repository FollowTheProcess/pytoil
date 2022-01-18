![logo](https://github.com/FollowTheProcess/pytoil/raw/main/docs/img/logo.png)

[![License](https://img.shields.io/github/license/FollowTheProcess/pytoil)](https://github.com/FollowTheProcess/pytoil)
[![PyPI](https://img.shields.io/pypi/v/pytoil.svg?logo=python)](https://pypi.python.org/pypi/pytoil)
[![GitHub](https://img.shields.io/github/v/release/FollowTheProcess/pytoil?logo=github&sort=semver)](https://github.com/FollowTheProcess/pytoil)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/FollowTheProcess/pytoil)
[![CI](https://github.com/FollowTheProcess/pytoil/workflows/CI/badge.svg)](https://github.com/FollowTheProcess/pytoil/actions?query=workflow%3ACI)
[![Coverage](https://github.com/FollowTheProcess/pytoil/raw/main/docs/img/coverage.svg)](https://github.com/FollowTheProcess/pytoil)

*pytoil is a small, helpful CLI to help developers manage their local and remote projects with ease!*

* **Source Code**: [https://github.com/FollowTheProcess/pytoil](https://github.com/FollowTheProcess/pytoil)

* **Documentation**: [https://FollowTheProcess.github.io/pytoil/](https://FollowTheProcess.github.io/pytoil/)

## What is it?

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

```shell
$ pipx install pytoil
---> 100%
Successfully installed pytoil
```

You can always fall back to pip

```shell
$ python3 -m pip install pytoil
---> 100%
Successfully installed pytoil
```

pytoil will install everything it needs *in python* to work. However, it's full feature set can only be accessed if you have the following external dependencies:

* [git]
* [conda] (if you work with conda environments)
* [VSCode] (if you want to use pytoil to automatically open your projects for you)
* [poetry] (if you want to create poetry environments)
* [flit] (if you want to create flit environments)

## Quickstart

`pytoil` is super easy to get started with.

After installation, the first time you run it it will make you a config file.

```shell
$ pytoil

No config file yet!
Making you a default one...
```

This will create a default config file which can be found at `~/.pytoil.yml`.

Don't worry though, there's only a few options to configure! :sleeping:

After you've set your config, you're good to go! You can do things like:

#### See your local and remote projects

```shell
$ pytoil show local
Local Projects

Showing 3 out of 3 local projects

  Name              Created          Modified
 ───────────────────────────────────────────────────
  project 1         13 days ago      9 days ago
  project 2         a day ago        a minute ago
  project 3         a month ago      a month ago
```

#### See which ones you have on GitHub, but not on your computer

```shell
$ pytoil show diff
Diff: Remote - Local

Showing 3 out of 3 projects

  Name             Size       Created                Modified
 ─────────────────────────────────────────────────────────────────────────
  remote 1         154.6 kB   a month ago            29 days ago
  remote 2         2.1 MB     1 year, 15 days ago    11 months ago
  remote 3         753.7 kB   1 year, 6 months ago   a month ago
```

#### Easily grab a project, regardless of where it is

```shell
$ pytoil checkout myproject

// Will now either open that project if local
// or clone it, then open it if not
```

#### Create a new project and virtual environment in one go

```shell
$ pytoil new myproject --venv venv

Creating project: 'myproject' at '/Users/you/projects/myproject'

Creating virtual environment for: 'myproject'
```

#### And even do this from a [cookiecutter] template

```shell
$ pytoil new myproject --venv venv --cookie https://github.com/some/cookie.git

Creating project: 'myproject' with cookiecutter template: 'https://github.com/some/cookie.git'

// You'll then be asked all the cookiecutter questions defined in the template
// After which pytoil will take over and create the virtual environment as normal
```

And loads more!

### Help

Like all good CLI programs, pytoil (as well as all it's subcommands, and all *their* subcommands!) has a `--help` option to show you what to do.

```shell
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
  checkout  Checkout an existing development project.
  config    Interact with pytoil's configuration.
  docs      Open pytoil's documentation in your browser.
  find      Quickly locate a project.
  gh        Open one of your projects on GitHub.
  info      Get useful info for a project.
  new       Create a new development project.
  pull      Pull down your remote projects.
  remove    Remove projects from your local filesystem.
  show      View your local/remote projects.
```

pytoil's CLI is designed such that if you don't specify any arguments, it won't do anything! just show you the `--help`. This is called being a 'well behaved' unix command line tool.

This is true for any subcommand of pytoil so you won't accidentally break anything if you don't specify arguments 🎉

And if you get truly stuck, you can quickly open pytoil's documentation with:

```shell
$ pytoil docs

Opening pytoil's documentation in your browser...

# Now you'll be on this page in whatever your default browser is!
```

Check out the [docs] for more 💥

## Contributing

`pytoil` is an open source project and, as such, welcomes contributions of all kinds 😃

Your best bet is to check out the [contributing guide] in the docs!

[pipx]: https://pipxproject.github.io/pipx/
[docs]: https://FollowTheProcess.github.io/pytoil/
[FollowTheProcess/poetry_pypackage]: https://github.com/FollowTheProcess/poetry_pypackage
[wasabi]: https://github.com/ines/wasabi
[httpx]: https://www.python-httpx.org
[async-click]: https://github.com/python-trio/asyncclick
[contributing guide]: https://followtheprocess.github.io/pytoil/contributing/contributing.html
[git]: https://git-scm.com
[conda]: https://docs.conda.io/en/latest/
[VSCode]: https://code.visualstudio.com
[config]: config.md
[cookiecutter]: https://github.com/cookiecutter/cookiecutter
[poetry]: https://python-poetry.org
[flit]: https://flit.readthedocs.io
