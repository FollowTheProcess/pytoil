# pytoil

[![License](https://img.shields.io/github/license/FollowTheProcess/pytoil)](https://github.com/FollowTheProcess/pytoil)
[![PyPI](https://img.shields.io/pypi/v/pytoil.svg)](https://pypi.python.org/pypi/pytoil)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/FollowTheProcess/pytoil)
[![CI](https://github.com/FollowTheProcess/pytoil/workflows/CI/badge.svg)](https://github.com/FollowTheProcess/pytoil/actions?query=workflow%3ACI)
[![Coverage](./img/coverage.svg)](https://github.com/FollowTheProcess/pytoil)

*pytoil is a small, helpful CLI to help developers manage their local and remote projects with ease!*

* **Source Code**: [https://github.com/FollowTheProcess/pytoil](https://github.com/FollowTheProcess/pytoil)

* **Documentation**: [https://FollowTheProcess.github.io/pytoil/](https://FollowTheProcess.github.io/pytoil/)

## What is it?

`pytoil` is a handy tool that helps you stay on top of all your projects, remote or local. It's primarily aimed at python developers but you could easily use it to manage any project!

pytoil is:

* Easy to use :white_check_mark:
* Easy to configure :white_check_mark:
* Safe (it won't edit your repos at all) :white_check_mark:
* Useful! (I hope :smiley:)

Say goodbye to janky bash scripts :wave:

## Installation

As pytoil is a CLI program, I'd recommend installing with [pipx]

```shell
pipx install pytoil
```

If you don't know what pipx is, go check it out!

You can always fall back to pip

```shell
pip install pytoil
```

!!! warning

    keep in mind though, you'll have to install it globally for it to work so it might be better to use pipx

## Quickstart

`pytoil` is super easy to get started with.

After installation just run

```shell
pytoil init
```

This will create a config file which can be found at `~/.pytoil.yml`, and will walk you through setting the tool up.

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
pytoil project checkout my_project
```

#### Create a new project and virtual environment in one go

```shell
pytoil project create my_project --venv virtualenv

```

#### And even do this from a [cookiecutter] template

```shell
pytoil project create my_project --venv virtualenv --cookiecutter https://github.com/some/cookie.git
```

[pipx]: https://pipxproject.github.io/pipx/
[cookiecutter]: https://cookiecutter.readthedocs.io/en/1.7.2/
