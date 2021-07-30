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

:warning: pytoil is still in Alpha and as such, the API may change without deprecation notices.

## What is it?

`pytoil` is a handy tool that helps you stay on top of all your projects, remote or local. It's primarily aimed at python developers but you could easily use it to manage any project!

pytoil is:

* Easy to use :white_check_mark:
* Easy to configure :white_check_mark:
* Safe (it won't edit your repos at all) :white_check_mark:
* Useful! (I hope :smiley:)

Say goodbye to janky bash scripts :wave:

## Installation

As pytoil is a CLI, I recommend [pipx]

```shell
pipx install pytoil
```

Or just pip (but must be globally available)

```shell
pip install pytoil
```

## Quickstart

`pytoil` is super easy to get started with.

After installation just run

```shell
$ pytoil config

No config file yet!
Making you a default one...
```

This will create a default config file which can be found at `~/.pytoil.yml`. See the [docs] for what information you need to put in here.

Don't worry though, there's only a few options to configure! :sleeping:

After that you're good to go! You can do things like:

#### See your local and remote projects

```shell
pytoil show all
```

#### See which ones you have on GitHub, but not on your computer

```shell
pytoil show diff
```

#### Easily grab a project, regardless of where it is

```shell
pytoil checkout my_project
```

#### Create a new project and virtual environment in one go

```shell
pytoil new my_project --venv venv

```

#### And even do this from a [cookiecutter] template

```shell
pytoil new my_project --venv venv --cookie https://github.com/some/cookie.git
```

Check out the [docs] for more :boom:

### Credits

This package was created with [cookiecutter] and the [FollowTheProcess/poetry_pypackage] project template.

`pytoil` has been built on top of these fantastic projects:

* [Typer]
* [cookiecutter]
* [wasabi]
* [httpx]
* [pydantic]

[pipx]: https://pipxproject.github.io/pipx/
[cookiecutter]: https://cookiecutter.readthedocs.io/en/1.7.2/
[docs]: https://FollowTheProcess.github.io/pytoil/
[FollowTheProcess/poetry_pypackage]: https://github.com/FollowTheProcess/poetry_pypackage
[Typer]: https://typer.tiangolo.com
[wasabi]: https://github.com/ines/wasabi
[httpx]: https://www.python-httpx.org
[pydantic]: https://pydantic-docs.helpmanual.io
