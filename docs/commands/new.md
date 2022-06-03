# New

`new` will make you a new project locally. You have the option to create a new virtual environment with it and to create the project from a [cookiecutter] template 🍪

## Help

<div class="termy">

```console
$ pytoil new --help

Usage: pytoil new [OPTIONS] PROJECT [PACKAGES]...

  Create a new development project.

  Bare usage will simply create an empty folder in your configured projects
  directory.

  You can also create a project from a cookiecutter or copier template by
  passing a valid url to the '--cookie/-c' or '--copier/-C' flags.

  If you just want a very simple, language-specific starting template, use the
  '--starter/-s' option.

  By default, pytoil will initialise a local git repo in the folder and commit
  it, following the style of modern language build tools such as rust's cargo.
  You can disable this behaviour by setting 'git' to false in pytoil's config
  file or by passing the '--no-git/-n' flag here.

  If you want pytoil to create a new virtual environment for your project, you
  can use the '--venv/-v' flag. Standard python and conda virtual environments
  are supported.

  If the '--venv/-v' flag is used, you may also pass a list of python packages
  to install into the created virtual environment. These will be delegated to
  the appropriate tool (pip or conda) depending on what environment was
  created. If the environment is conda, the packages will be passed at
  environment creation time meaning they will have their dependencies resolved
  together. Normal python environments will first be created and then have
  specified packages installed.

  If 'common_packages' is specified in pytoil's config file, these will
  automatically be included in the environment.

  To specify versions of packages via the command line, you must enclose them
  in double quotes e.g. "flask>=1.0.0" not flask>=1.0.0 otherwise this will be
  interpreted by the shell as a command redirection.

  Examples:

  $ pytoil new my_project

  $ pytoil new my_project --cookie https://github.com/some/cookie.git

  $ pytoil new my_project --venv conda

  $ pytoil new my_project -c https://github.com/some/cookie.git -v conda --no-
  git

  $ pytoil new my_project -v venv requests "flask>=1.0.0"

  $ pytoil new my_project --starter python

Options:
  -c, --cookie TEXT               URL to a cookiecutter template from which to
                                  build the project.
  -C, --copier TEXT               URL to a copier template from which to build
                                  the project.
  -s, --starter [python|go|rust]  Use a language-specific starter template.
  -v, --venv [venv|conda]         Which type of virtual environment to create.
  -n, --no-git                    Don't do any git stuff.
  --help                          Show this message and exit.
```

</div>

## No Options

If you don't give any options, the default behaviour is to just make a new empty folder with no virtual environment for you to do whatever you want with!

In this sense, you don't have to be a python developer to use pytoil!

<div class="termy">

```console
$ pytoil new my_new_project

Creating new project: 'my_new_project'
// Does some stuff...
```

</div>

### New Git Repo

By default, pytoil will also create a local git repository in this folder for you. You can disable this behaviour by changing the value for `git` in your config file, or on a per use basis by using the `--no-git` flag.

You will need `git` installed to be able to use this feature.

<div class="termy">

```console
$ pytoil new my_new_project --no-git

Creating new project: 'my_new_project'
// Does some stuff...but not git
```

</div>

!!! note

    A lot of modern language tools (e.g. rust's `cargo`) initialise a git repo by default and I liked the idea so here it is :smiley:

## Include Virtual Environment

If you are a python developer though, chances are you'll want to create a virtual environment with your project. pytoil supports both [venv] and [conda] environments, although for the latter you'll have to have the conda package manager already installed on your system. I personally recommend [miniconda] as you get the package manager but none of the bundled packages (which can be quite large!).

For standard python virtual environments, pytoil uses the standard library `venv` module so you don't need to install anything external.

If you want to use conda environments though, you'll need to have a `conda` package manager installed and available on $PATH.

!!! info

    If you don't know what conda is: as a general rule, you'll want to use venv on most python projects (particularly packages i.e. things that can be pip installed). If you do a lot of work with data (think pandas, numpy, scikit-learn) you'll probably want to use conda as a lot of python data tools include native C libraries which require compiling, and conda makes this happen seamlessly :nerd_face:

Pytoil has been tested and supports the following conda distributions:

* Anaconda
* Miniconda
* Miniforge
* Mambaforge

All you have to do is specify which virtual environment to create, using the `--venv/-v` option flag. You can choose from `venv` or `conda`. The default is `None`.

<div class="termy">

```console
$ pytoil new my_new_project --venv venv

Creating new project: 'my_new_project'
Creating virtual environment for: 'my_new_project'
```

</div>

Or with conda...

<div class="termy">

```console
$ pytoil new my_new_project --venv conda

Creating new project: 'my_new_project'
Creating conda environment for: 'my_new_project'
// Conda environments typically take a bit longer to make as it has to do a bit more work!
```

</div>

## Install Packages at Creation

A blank virtual environment isn't really much use yet! `pytoil` lets you inject packages at environment creation time! All you have to do is pass packages you want to install into the new environment as additional command line arguments and pytoil will figure this all out for you.

<div class="termy">

```console
$ pytoil new my_new_project --venv conda pandas numpy scikit-learn

Creating new project: 'my_new_project'
Creating conda environment for: 'my_new_project'
Including packages: pandas, numpy, scikit-learn
// Conda environments typically take a bit longer to make as it has to do a bit more work!
```

</div>

!!! note

    This is also where the `common_packages` setting from the config file comes in! If you specify packages here, these will automatically get injected into every environment pytoil creates, whether its a python virtual environment or a conda environment. This is particularly useful for development dependencies like linters and formatters etc.

## Build a project from a Cookiecutter/Copier Template

If you don't know what [cookiecutter] or [copier] are, go and check them out! Essentially, they are templating engines for development projects and, after asking you a few questions, can dynamically insert and modify text inside your project, set up directory structure and all sorts of cool automation stuff!

It means that if you find a template you like (or make your own) you can use it as the base for development projects without having to create so much boilerplate at the beginning, they're great :thumbsup:

Because I love these projects so much, I built pytoil to support them easily. You can create a new project from a cookiecutter or copier template by using the `--cookie/-c` or `--copier/-C` flag like this:

<div class="termy">

```console
// Just pass a url to a cookiecutter template
$ pytoil new my_new_project --cookie https://github.com/some/cookie.git

Creating new project: 'my_new_project' from cookiecutter: 'https://github.com/some/cookie.git'
```

</div>

## Create from a starter

pytoil also comes with a few basic starter templates for some common languages. How it creates these templates is specific to the language, but you can use them like this....

Here's a python one:

<div class="termy">

```console
// Just pass a valid starter
$ pytoil new my_new_python_project --starter python

Creating new project: 'my_new_python_project' from starter: 'python'
```

</div>

And with go:

<div class="termy">

```console
// Just pass a valid starter
$ pytoil new my_new_go_project --starter go

Creating new project: 'my_new_go_project' from starter: 'go'
```

</div>

!!! note

    Currently pytoil supports python, go and rust starter templates. The starters are super easy to implement though so if you want more languages supported, maybe throw us a PR :wink:

The table below shows what happens under the hood when a starter is given to `pytoil new`:

|        Starter    |                                              Implementation                                           |
| :---------------: | :---------------------------------------------------------------------------------------------------: |
|     `python`      |                              Creates everything internally using pathlib                              |
|       `go`        |               Creates the root directory and main.go internally. Then calls `go mod init`             |
|      `rust`       |                        Creates the root directory internally. Then calls `cargo init`                 |

## All in One Go

Because pytoil uses [async-click] for it's CLI, the arguments and options to CLI commands are all resolved really intelligently so you can specify all of them in one go if you like to get complex behaviour!

<div class="termy">

```console
$ pytoil new my_new_project --cookie https://github.com/some/cookie.git --venv venv --no-git requests "flask>=1.0.0" sqlalchemy

// Many things will now happen!
```

</div>

In this snippet we've:

* Created a new project in the correct folder called 'my_new_project'
* Built this project from a cookiecutter template hosted on GitHub
* Created a fresh python virtual environment for the project
* Told pytoil not to initialise an empty git repo (it actually doesn't do this on cookiecutter projects anyway but you get the point)
* Passed a list of additional packages to install into the new environment (along with any we've specified in the config file)

That's better than doing all this yourself isn't it! :thumbsup:

[cookiecutter]: https://cookiecutter.readthedocs.io/en/1.7.2/
[copier]: https://copier.readthedocs.io/en/latest/
[venv]: https://docs.python.org/3/library/venv.html
[conda]: https://docs.conda.io/en/latest/
[miniconda]: https://docs.conda.io/en/latest/miniconda.html
[click]: https://click.palletsprojects.com/en/8.1.x/
