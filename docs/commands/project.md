# Project

Now let's look at the commands you'll use to manage projects.

!!! tip

    Remember, each subcommand has its own help you can check out too. e.g. `pytoil new --help` :thumbsup:

## New

`new` will make you a new project locally. You have the option to create a new virtual environment with it and to create the project from a [cookiecutter] template :cookie:

### No Options

If you don't give any options, the default behaviour is to just make a new empty folder with no virtual environment for you to do whatever you want with!

In this sense, you don't have to be a python developer to use pytoil!

<div class="termy">

```console
$ pytoil new my_new_project

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
$ pytoil new my_new_project --venv virtualenv

Creating new project: 'my_new_project'
Creating virtualenv for: 'my_new_project'
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

### Build a project from a Cookiecutter Template

If you don't know what [cookiecutter] is, go and check them out! Essentially, it is a templating engine for development projects and, after asking you a few questions, it can dynamically insert and modify text inside your project, set up directory structure and all sorts of cool automation stuff!

It means that if you find a template you like (or make your own) you can use it as the base for development projects without having to create so much boilerplate at the beginning, they're great :thumbsup:

!!! note

    In fact, pytoil was itself started from a cookiecutter template!

Because I love cookiecutter so much, I built pytoil to support them easily. You can create a new project from a cookiecutter template by using the `--cookie/-c` flag like this:

<div class="termy">

```console
// Just pass a url to a cookiecutter template
$ pytoil new my_new_project --cookie https://github.com/some/cookie.git

Creating new project: 'my_new_project' from cookiecutter: 'https://github.com/some/cookie.git'
```

</div>

## Info

This one's easy! `info` simply shows you some summary information about whatever project you tell it to.

<div class="termy">

```console
// Let's get some info about pytoil
$ pytoil info pytoil

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
$ pytoil info my_local_project

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
$ pytoil checkout my_local_project

Project: 'my_local_project' found locally!

Opening 'my_github_project' in VSCode...
```

</div>

If not, `checkout` will:

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

If you pass the `--venv` option, `checkout` will also:

* Try to detect what environment would work best for the project (conda or virtualenv)
* Auto create this virtual environment and install any configured common packages
* If you have VSCode configured, `pytoil` will also set your workspace `python.pythonPath`

<div class="termy">

```console
// Some project thats on GitHub
$ pytoil checkout my_github_project --venv

Project: 'my_github_project' found on GitHub! Cloning...
// You might see some git clone output here

Auto-creating correct virtual environment
// Here you might see some conda or virtualenv stuff

Opening 'my_github_project' in VSCode...
```

</div>

!!! note
    
    pytoil looks for certain files in your project (like `setup.py`, `setup.cfg`, `environment.yml` etc.) and that's how it decides which environment to create. If it isn't totally sure what environment to create, it will just skip this step and let you know!

## Remove

Another easy one! `remove` does exactly what it says. It will recursively delete an entire project from your local projects directory. Since this is quite a destructive action, pytoil will prompt you to confirm before it does anything. If you say no, the entire process will be aborted and your project will be left alone!

!!! warning

    The deletion of a project like this is irreversible. It does not send the folder to Trash, it simply erases it from all existence in the universe, so make sure you know what you're doing before saying yes! :scream:

!!! success "Don't Panic!"

    Don't worry though, `remove` **DOES NOT** go near anything on your GitHub, only your local directories are affected by `remove`. pytoil only makes HTTP GET requests to the GitHub API so you couldn't even delete a repo if you wanted to, in fact you can't make any changes to any GitHub repo with pytoil whatsoever so you're completely safe! :grin:

<div class="termy">

```console
$ pytoil remove my_project

# This will remove ['my_project'] from your local filesystem. Are you sure? [y/N]:$ y

Removing project: 'my_project'.

Done!
```

</div>

And if you say no...

<div class="termy">

```console
$ pytoil remove my_project

# This will remove ['my_project'] from your local filesystem. Are you sure? [y/N]:$ n

Aborted!
```

</div>

`remove` also accepts a list of projects if you want to remove a few in one go:

<div class="termy">

```console
$ pytoil remove remove1 remove2 remove3 remove4

# This will remove ['remove1', 'remove2', 'remove3'] from your local filesystem. Are you sure? [y/N]:$ y

Removing project: 'remove1'.
Removing project: 'remove2'.
Removing project: 'remove3'.

Done!
```

</div>

And if you've completely given up and decided you don't want to be a developer anymore (we've all been there), you can erase all your local projects:

<div class="termy">

```console
$ pytoil remove --all

# This will remove all your projects. Are you okay? [y/N]:$ y

Removing project: 'remove1'.
Removing project: 'remove2'.
Removing project: 'remove3'.

Done!
```

</div>

## gh

Sometimes you just want to quickly go to the GitHub page for your project. Enter the incredibly simple `gh` command!

<div class="termy">

```console
$ pytoil gh my_project

Opening 'my_project' in your browser...

// Now you're at the GitHub page for the project!
```

</div>

[cookiecutter]: https://cookiecutter.readthedocs.io/en/1.7.2/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[conda]: https://docs.conda.io/en/latest/
[miniconda]: https://docs.conda.io/en/latest/miniconda.html
[config]: ../config.md
[pathlib]: https://docs.python.org/3/library/pathlib.html
