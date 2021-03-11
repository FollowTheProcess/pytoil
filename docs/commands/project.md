# Project

Now let's look at the `project` subcommand. This is the biggest subcommand in pytoil and probably the part you'll interact with the most. Again, we'll start with the help.

## Help

<div class="termy">

```console
$ pytoil project --help

Usage: pytoil project [OPTIONS] COMMAND [ARGS]...

  Operate on a specific project.

  Set the "projects_dir" key in the config to control where this command
  looks on your local file system.

  Set the "token" key in the config to give pytoil access to your GitHub via
  the API.

  We only make GET requests, your repos are safe with pytoil!

Options:
  --help  Show this message and exit.

Commands:
  checkout  Checkout a development project, either locally or from GitHub.
  create    Create a new development project locally.
  info      Show useful information about a project.
  remove    Deletes a project from your local filesystem.
```

</div>

!!! tip

    Remember, each subcommand has its own help you can check out too. e.g. `pytoil project create --help` :thumbsup:

## Create

`create` will make you a new project locally. You have the option to create a new virtual environment with it and to create the project from a [cookiecutter] template :cookie:

### No Options

If you don't give any options, the default behaviour is to just make a new empty folder with no virtual environment for you to do whatever you want with!

In this sense, you don't have to be a python developer to use pytoil!

<div class="termy">

```console
$ pytoil project create my_new_project

Creating new project: 'my_new_project'
// Does some stuff...
```

</div>

### Include Virtual Environment

If you are a python developer though, chances are you'll want to create a virtual environment with your project. pytoil supports both [virtualenv] and [conda] environments, although for the latter you'll have to have the conda package manager already installed on your system. I personally recommend [miniconda] as you get the package manager but none of the bundled packages (which can be quite large!).

!!! info

    If you don't know what conda is: as a general rule, you'll want to use virtualenv on most python projects (particularly packages i.e. things that can be pip installed). If you do a lot of work with data (think pandas, numpy, scikit-learn) you'll probably want to use conda as a lot of python data tools include native C libraries which require compiling, and conda makes this happen seamlessly :nerd_face:

All you have to do is specify which virtual environment to create, using the `--venv/-v` option flag. You can choose from `virtualenv` or `conda`. The default is `None`.

<div class="termy">

```console
$ pytoil project create my_new_project --venv virtualenv

Creating new project: 'my_new_project'
Creating virtualenv for: 'my_new_project'
```

</div>

Or with conda...

<div class="termy">

```console
$ pytoil project create my_new_project --venv conda

Creating new project: 'my_new_project'
Creating conda environment for: 'my_new_project'
// Conda environments typically take a bit longer to make as it has to do a bit more work!
```

</div>

### Build a project from a Cookiecutter Template

If you don't know what [cookiecutter] is, go and check them out! Essentially, it is a templating engine for development projects and, after asking you a few questions, it can dynamically insert and modify text inside your project, set up directory structure and all sorts of cool automation stuff!

It means that if you find a template you like (or make your own) you can use it as the base for development projects without having to create so much boilerplate at the beginning, they're great :thumbsup:

!!! note

    In fact, pytoil was itself started from a cookiecutter template!

Because I love cookiecutter so much, I built pytoil to support them easily. You can create a new project from a cookiecutter template by using the `--cookie/-c` flag like this:

<div class="termy">

```console
// Just pass a url to a cookiecutter template
$ pytoil project create my_new_project --cookie https://github.com/some/cookie.git

Creating new project: 'my_new_project' from cookiecutter: 'https://github.com/some/cookie.git'
```

</div>

## Info

This one's easy! `info` simply shows you some summary information about whatever project you tell it to.

<div class="termy">

```console
// Let's get some info about pytoil
$ pytoil project info pytoil

Info for: pytoil

name: pytoil
description: CLI to automate the development workflow.
created_at: 2021-02-04T15:05:23Z
updated_at: 2021-03-02T11:09:08Z
size: 219
license: Apache License 2.0
remote: True
local: True
```

</div>

What happens here is pytoil uses the GitHub personal access token we talked about in [config] and hits the GitHub API to find out some basic information about the repo you pass to it :white_check_mark:

pytoil will always prefer this way of doing it as we can get things like license information and description which is a bit more helpful to show. If however, the project you're asking for information about does not exist on GitHub yet, you'll still get some info back!

<div class="termy">

```console
// Some project thats not on GitHub yet
$ pytoil project info my_local_project

Info for: my_local_project

name: my_local_project
created_at: 2021-02-27 12:37:18
updated_at: 2021-02-27 12:48:18
size: 256
local: True
remote: False
```

</div>

!!! note

    pytoil grabs this data from your operating system by using the `Path.stat()` method from [pathlib] :computer:

## Checkout

`checkout` (not to be confused with `git checkout`) allows to easily resume work on an ongoing development project.

If the project is available locally, `checkout` will simply open it for you

<div class="termy">

```console
// Some project thats already local
$ pytoil project checkout my_local_project

Project: 'my_local_project' found locally!

Opening 'my_github_project' in VSCode...
```

</div>

If not, `checkout` will:

* Clone it to your projects directory
* Detect what type of project it is (conda or virtualenv)
* Create the required virtual environment for you automatically
* Open it for you (if you configure VSCode in [config])

<div class="termy">

```console
// Some project thats on GitHub
$ pytoil project checkout my_github_project

Project: 'my_github_project' found on GitHub! Cloning...
// You might see some git clone output here

Auto-creating correct virtual environment
// Here you might see some conda or virtualenv stuff

Opening 'my_github_project' in VSCode...
```

</div>

!!! info "Why just VSCode?"

    When developing pytoil I was debating how to handle this. I use VSCode for everything but I know other people have different editor preferences. Initially I looked at using the `$EDITOR` environment variable but working how best to launch a variety of possible editors from a CLI was tricky. Plus pytoil does things like alter workspace settings to point at the right virtual environment, and I only know how to do this with VSCode.

    PR's are very welcome though if you think you can introduce support for your preferred editor! :grin:

## Remove

Another easy one! `remove` does exactly what it says. It will recursively delete an entire project from your local projects directory. Since this is quite a destructive action, pytoil will prompt you to confirm before it does anything. If you say no, the entire process will be aborted and your project will be left alone!

!!! warning

    The deletion of a project like this is irreversible. It does not send the folder to Trash, it simply erases it from all existence in the universe, so make sure you know what you're doing before saying yes! :scream:

!!! success "Don't Panic!"

    Don't worry though, `remove` **DOES NOT** go near anything on your GitHub. pytoil only makes HTTP GET requests to the GitHub API so you couldn't even delete a repo if you wanted to, in fact you can't make any changes to any GitHub repo with pytoil whatsoever so you're completely safe! :grin:

<div class="termy">

```console
$ pytoil project remove my_project

# This will remove 'my_project' from your local filesystem. Are you sure? [y/N]:$ y

Removing project: 'my_project'.

Done!
```

</div>

And if you say no...

<div class="termy">

```console
$ pytoil project remove my_project

# This will remove 'my_project' from your local filesystem. Are you sure? [y/N]:$ n

Aborted!
```

</div>

[cookiecutter]: https://cookiecutter.readthedocs.io/en/1.7.2/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[conda]: https://docs.conda.io/en/latest/
[miniconda]: https://docs.conda.io/en/latest/miniconda.html
[config]: ../config.md
[pathlib]: https://docs.python.org/3/library/pathlib.html
