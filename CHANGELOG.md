# Changelog

## 0.2.dev

* NEW: User can now specify a list of packages to inject into every environment pytoil creates
* Internal config management now far simpler, makes changing or adding configurable features much easier
* pytoil config CLI drastically simplified
* NEW: Added `pytoil docs` command to open the package documentation in users default browser

## 0.2.0

* FIX: `pytoil init` now gracefully exits on ctrl+c preventing a bug where if a user aborted halfway through, the config file would appear to have been written but would not be valid and raise an ugly error on next use.
* NEW: All commands that were in `pytoil project` are now available from the root command. E.g. instead of typing `pytoil project checkout` you may now simply use `pytoil checkout`.

## 0.1.0

* First release.
