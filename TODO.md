# Pytoil 2.0

This is the dev repo for pytoil 2.0 (it won't actually be 2.0 but ya know).

## Enhancements

- [x] On creating a new project with a virtual environment, user should be able to pass a list of packages to install
- [x] Add "init_on_new" to config file to control whether or not pytoil initialises a new git repo in new projects
- [x] Use wasabi for nicer printing
- [x] Add all known conda environment directories to env dispatcher (e.g. miniconda3, miniforge3, mambaforge etc.)
- [x] If GitHub token isn't set in config file, try and get $GITHUB_TOKEN instead. Only if that isn't present fail, but fail nicely.
- [ ] Full requirements file resolving like my custom shell functions do

## Fixes

- [x] Original pytoil would give a messy error on missing config file, make this one just print a nice looking warning and exit anytime this happens
- [x] Only show repos user has direct ownership of, not org repos
