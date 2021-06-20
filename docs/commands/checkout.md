# Checkout

`checkout` (not to be confused with `git checkout`) allows to easily resume work on an ongoing development project.

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
* If you have VSCode configured, `pytoil` will also set your workspace `python.pythonPath`

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
