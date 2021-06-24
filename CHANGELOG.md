# Changelog

## 0.dev

* NEW: User can now initialise basic starter templates for multiple languages (currently support python, go and rust)

## 0.5.0

Complete rewrite from the ground up!

* NEW: pytoil now supports a variety of conda installations
* NEW: `pytoil sync` changed to `pytoil pull`
* NEW: User can configure whether or not to create a git repo on `new`
* NEW: Additional packages can now be passed in as extra arguments when creating an environment with `pytoil new`
* NEW: Friendlier output to the user during operations and awesome loading spinners
* NEW: Output from invoked external tools is now captured and only surfaced when something goes wrong
* NEW: If `$GITHUB_TOKEN` is present in the environment, pytoil will fall back to that if `token` is not set in the config file
* NEW: User can now interact with the config file via the tool itself

* FIX: pytoil now handles common errors much nicer (missing config file, bad github token etc.)
* FIX: Much better error handling all round

* CLN: Complete internal rewrite, better cohesion and looser coupling
* CLN: Less reliance on mocks during tests

* MAINT: Project build tool switched to poetry

Probably more but I forget.

## 0.4.2

* NEW: pytoil now supports the use of miniforge as a conda installation
* CLN: Some minor refactorings and code clean up

## 0.4.1

* NEW: `pytoil checkout` default behaviour changed to not create virtual environment. Now available through the `--venv` option bringing it in line with `pytoil new`
* Various meta project tweaks and tidying up

## 0.4.0

* NEW: `pytoil create` changed to `pytoil new`

## 0.3.2

* BUG: Fix bug where `pytoil info` on a repo with no OSS license would cause an error. Now just displays `None` for `license`.

## 0.3.1

* NEW: `pytoil remove` now accepts list of projects to remove
* NEW: `pytoil create` now initialises an empty git repo in non-cookiecutter projects
* NEW: `pytoil remove` now accepts a `--all` flag to remove all projects from local directory

## 0.3.0

* NEW: User can now specify a list of packages to inject into every environment pytoil creates
* Internal config management now far simpler, makes changing or adding configurable features much easier
* pytoil config CLI drastically simplified
* NEW: Added `pytoil docs` command to open the package documentation in users default browser
* NEW: Added `pytoil gh` command to open the GitHub page for a project.

## 0.2.0

* FIX: `pytoil init` now gracefully exits on ctrl+c preventing a bug where if a user aborted halfway through, the config file would appear to have been written but would not be valid and raise an ugly error on next use.
* NEW: All commands that were in `pytoil project` are now available from the root command. E.g. instead of typing `pytoil project checkout` you may now simply use `pytoil checkout`.

## 0.1.0

* First release.
