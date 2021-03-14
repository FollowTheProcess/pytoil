# TODO

Below are a list of enhancements or fixes discovered during pre-release testing:

## Longer Term Enhancements

### Hot

- [ ] Make it automatically install requirements if a file present. For setuptools this could be one or more of `requirements.txt`, `requirements_dev.txt`, `requirements/dev.txt`, `setup.py`, or `setup.cfg`. The latter two requiring parsing of files to get to what we want. For conda this will simply be `environment.yml`.
- [ ] Make it so you can pass packages to create that will be installed into the virtual environment after creation (or during creation for conda). This is tricky to do with the current implementation as this would have to be in `pytoil project create` as an option like `--packages` or something and currently in Typer you can't pass a list to an option without doing something like this: `pytoil project create --venv virtualenv --packages package1 --packages package2 etc.`
- [ ] Everything being under project feels clunkier than I thought it would. Would be good if we could instead do `pytoil checkout` `pytoil create` etc. rather than `pytoil project checkout`. If I remember right though, there are some issues doing this with Typer, everything to do with projects would have to live in `main.py` which might get messy.
- [ ] Specify (in the config file) some packages to install in every environment pytoil creates. This is most useful for things like linters and formatters etc that you wan't in every project.

### Warm

- [ ] Add support for poetry? Need to add entry to config file. If checkout project contains a `pyproject.toml` which references [tool.poetry] then use `poetry install` to create the environment.

### Cold

- [ ] Add a config check command that more closely inspects the config file and does some validation
- [ ] Option to make a git repo on create, maybe a GitHub repo too and link them? Or is this better left to the gh cli?
- [ ] Add pytoil remove --all option to completely clear projects directory
