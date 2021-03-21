# TODO

Below are a list of enhancements or fixes discovered during pre-release testing:

## Longer Term Enhancements

### Hot

- [ ] Make it automatically install requirements if a file present. For setuptools this could be one or more of `requirements.txt`, `requirements_dev.txt`, `requirements/dev.txt`, `setup.py`, or `setup.cfg`. The latter two requiring parsing of files to get to what we want. For conda this will simply be `environment.yml`.

### Warm

- [ ] Add support for poetry? Need to add entry to config file. If checkout project contains a `pyproject.toml` which references [tool.poetry] then use `poetry install` to create the environment.
- [x] Make `pytoil remove` accept a list of local projects not just a single one
- [ ] Make `pytoil create` initialise a new git repo, inspired by things like `cargo new` which does the same. Maybe configurable?

### Cold

- [ ] Add pytoil remove --all option to completely clear projects directory
