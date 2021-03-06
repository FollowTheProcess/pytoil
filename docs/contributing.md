# Contributing to pytoil

I've tried to structure pytoil to make it nice and easy for people to contribute. Here's how to go about doing it! :smiley:

## Developing

If you want to fix a bug, improve the docs, add tests, add a feature or any other type of direct contribution to pytoil: here's how you do it!

**To work on pytoil you'll need python >=3.8**

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

The easiest way to get your development environment set up is run the `dev` makefile target:

```shell
make dev
```

This will create a virtual environment for you (if it doesn't already exist), install pytoil's dependencies, install pytoil itself in editable mode so you can work on it and install the pre-commit hooks to catch pesky mistakes!

If you want to do this manually though, just do the following:

```shell
# Make the environment and activate it
python3 -m venv .venv
source .venv/bin/activate

# Upgrade important stuff (tends to reduce install bugs etc.)
python3 -m pip install --upgrade pip setuptools wheel

# Install pytoil and it's development dependencies
python3 -m pip install -e .[dev]

# If you use zsh you might have to escape the square brackets
python3 -m pip install -e .\[dev\]

# Install pre-commit hooks
pre-commit install
```

### Step 5: Do your thing

**Always checkout a new branch before changing anything**

```shell
git checkout -b <name-of-your-bugfix-or-feature>
```

Now you're ready to start working!

!!! tip

    Remember! pytoil aims for high test coverage. If you implement a new feature, make sure to write tests for it! Similarly, if you fix a bug, it's good practice to write a test that would have caught that bug so we can be sure it doesn't reappear in the future!

pytoil uses [nox] for automated testing, building the docs, formatting and linting etc. So when you've made your changes, just run:

```shell
nox
```

And it will tell you if something's wrong!

Nox does everything in fresh virtual environments so it's a great tool but sometimes you want quicker feedback on test results. For this, I've included a makefile with little tasks like test, coverage etc.

To run the tests this way:

```shell
make test
```

Run `make help` to see the tasks and the description of what they do

### Step 6: Commit your changes

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

### Step 7: Create a Pull Request

Now go to the original pytoil [repo] and create a Pull Request. Make sure to choose upstream repo "main" as the destination branch and your forked repo "your-branch-name" as the source.

Thats it! Your code will be tested automatically by pytoil's CI suite and if everything passes and your PR is approved and merged then it will become part of pytoil!

*Note: There is a good guide to open source contribution workflow [here] and also [here too]*

## Contributing to Docs

Any improvements to the documentation are always appreciated! pytoil uses [mkdocs] with the [mkdocs-material] theme so the documentation is all written in markdown and can be found in the `docs` folder in the project root.

Because pytoil uses [nox], things like building and serving the documentation is super easy. All you have to do is:

```shell
# Builds the docs
nox -s docs

# Or again, the makefile
make docs

# Builds and serves to localhost
nox -s docs -- serve

# makefile equivalent
make autodocs
```

If you use the `serve` option, you can navigate to the localhost IP address it gives you and as you make changes to the source files, it will automatically reload your browser! Automation is power! :robot:

If you add pages to the docs, make sure they are placed in the nav tree in the `mkdocs.yml` file and you're good to go!

!!! note

    There is also a makefile with some handy tasks built in if you want to run them quickly. Things like `make test` and `make docs`.

    But you'll have to have the virtual environment activated to run these!

[GH CLI]: https://cli.github.com
[nox]: https://nox.thea.codes/en/stable/
[repo]: https://github.com/FollowTheProcess/pytoil
[here]: https://stackoverflow.com/questions/20956154/whats-the-workflow-to-contribute-to-an-open-source-project-using-git-pull-reque
[here too]: https://github.com/asmeurer/git-workflow
[mkdocs]: https://www.mkdocs.org
[mkdocs-material]: https://squidfunk.github.io/mkdocs-material/
