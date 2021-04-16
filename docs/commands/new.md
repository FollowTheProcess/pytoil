# New

`new` will make you a new project locally. You have the option to create a new virtual environment with it and to create the project from a [cookiecutter] template :cookie:

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

## Include Virtual Environment

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

## Build a project from a Cookiecutter Template

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

[cookiecutter]: https://cookiecutter.readthedocs.io/en/1.7.2/
[virtualenv]: https://virtualenv.pypa.io/en/latest/
[conda]: https://docs.conda.io/en/latest/
[miniconda]: https://docs.conda.io/en/latest/miniconda.html
