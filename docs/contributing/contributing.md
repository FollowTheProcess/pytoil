# Contributing to pytoil

I've tried to structure pytoil to make it nice and easy for people to contribute. Here's how to go about doing it! :smiley:

!!! note

    All contributors must follow the [Code of Conduct](code_of_conduct.md)

## Developing

If you want to fix a bug, improve the docs, add tests, add a feature or any other type of direct contribution to pytoil: here's how you do it!

**To work on pytoil you'll need python >=3.9**

### Step 1: Fork pytoil

The first thing to do is 'fork' pytoil. This will put a version of it on your GitHub page. This means you can change that fork all you want and the actual version of pytoil still works!

To create a fork, go to the pytoil [repo] and click on the fork button!

### Step 2: Clone your fork

Navigate to where you do your development work on your machine and open a terminal

**If you use HTTPS:**

```shell
git clone https://github.com/<your_github_username>/pytoil.git
```

**If you use SSH:**

```shell
git clone git@github.com:<your_github_username>/pytoil.git
```

**Or you can be really fancy and use the [GH CLI]**

```shell
gh repo clone <your_github_username>/pytoil
```

HTTPS is probably the one most people use!

Once you've cloned the project, cd into it...

```shell
cd pytoil
```

This will take you into the root directory of the project.

Now add the original pytoil repo as an upstream in your forked project:

```shell
git remote add upstream https://github.com/FollowTheProcess/pytoil.git
```

This makes the original version of pytoil `upstream` but not `origin`. Basically, this means that if your working on it for a while and the original project has changed in the meantime, you can do:

```shell
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

This will (in order):

* Checkout the main branch of your locally cloned fork
* Fetch any changes from the original project that have happened since you forked it
* Merge those changes in with what you have
* Push those changes up to your fork so your fork stays up to date with the original.

!!! note

    Good practice is to do this before you start doing anything every time you start work, then the chances of you getting conflicting commits later on is much lower!

### Step 3: Create the Environment

Before you do anything, you'll want to set up your development environment...

pytoil uses [hatch] for project management and task automation.

I recommend using [pipx] for python command line tools like these, it installs each tool in it's own isolated environment but exposes the command to your terminal as if you installed it globally. To install [hatch] with pipx:

```shell
pipx install hatch
```

To get started all you need to do is run:

```shell
hatch env create
```

When you run this, hatch will create a virtual environment for you and install all the dependencies you need to develop pytoil

Not bad for a single command! Doing it this way means that before you start working on pytoil you know its all been installed and works correctly.

Wait for it to do it's thing and then you can get started.

!!! tip

    If you run `hatch env show` it will show you all the different environments and the things you can do in them.

### Step 4: Do your thing

**Always checkout a new branch before changing anything**

```shell
git switch --create <name-of-your-bugfix-or-feature>
```

Now you're ready to start working!

*Remember! pytoil aims for high test coverage. If you implement a new feature, make sure to write tests for it! Similarly, if you fix a bug, it's good practice to write a test that would have caught that bug so we can be sure it doesn't reappear in the future!*

The tasks for automated testing, building the docs, formatting and linting etc. are all defined in [hatch] So when you've made your changes, just run:

```shell
hatch run check
```

And it will tell you if something's wrong!

### Step 5: Commit your changes

Once you're happy with what you've done, add the files you've changed:

```shell
git add <changed-file(s)>

# Might be easier to do
git add -A

# But be wary of this and check what it's added is what you wanted..
git status
```

Commit your changes:

```shell
git commit

# Now write a good commit message explaining what you've done and why.
```

While you were working on your changes, the original project might have changed (due to other people working on it). So first, you should rebase your current branch from the upstream destination. Doing this means that when you do your PR, it's all compatible:

```shell
git pull --rebase upstream main
```

Now push your changes to your fork:

```shell
git push origin <your-branch-name>
```

### Step 6: Create a Pull Request

Now go to the original pytoil [repo] and create a Pull Request. Make sure to choose upstream repo "main" as the destination branch and your forked repo "your-branch-name" as the source.

That's it! Your code will be tested automatically by pytoil's CI suite and if everything passes and your PR is approved and merged then it will become part of pytoil!

!!! note

    There is a good guide to open source contribution workflow [here] and also [here too]

## Contributing to Docs

Any improvements to the documentation are always appreciated! pytoil uses [mkdocs] with the [mkdocs-material] theme so the documentation is all written in markdown and can be found in the `docs` folder in the project root.

Because pytoil uses [hatch], things like building and serving the documentation is super easy. All you have to do is:

```shell
# Builds the docs
hatch run docs:build

# Builds and serves
hatch run docs:serve
```

If you use the `serve` option, you can navigate to the localhost IP address it gives you and as you make changes to the source files, it will automatically reload your browser! Automation is power! :robot:

If you add pages to the docs, make sure they are placed in the nav tree in the `mkdocs.yml` file and you're good to go!

[GH CLI]: https://cli.github.com
[repo]: https://github.com/FollowTheProcess/pytoil
[mkdocs]: https://www.mkdocs.org
[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/
[pipx]: https://pypa.github.io/pipx/installation/
[hatch]: https://hatch.pypa.io/latest/
