# pytoil's TODO

## Fixes

- [ ] `pytoil checkout` fails if cloning a repo from an org the user has access to

## Tweaks & Refactors

- [ ] Tweak how `Config` works such that every object/method that needs a `Config` can either have it's required arguments passed in directly into the method, or use the passed in `Config` object. This should eliminate a lot of mocking complexity in the tests and make sure we don't need to keep calling `config.get` everywhere that needs it which is IO expensive.
- [x] Support `$HOME/miniforge3` for conda environments. M1 mac users will have to use miniforge for conda, this should be supported.
- [x] `pytoil remove` shows the actual set object on confirm i.e. `{project1, project2}`. Would be nicer if it just showed the normal comma separated list of projects like `project1, project2`.
- [ ] Things like `pytoil remove` and `pytoil sync` have an `all` action but it's inconsistent. In `remove` it's `--all` but in sync it's command `all`. Make both an option `--all`.

## Essentials

- [ ] If creating a virtual environment on `checkout` should have some logic to detect the presence of requirements files and automatically install them into the environment. So like `pip install -r requirements.txt` or `pip install -e .[dev]` etc. Some assumptions may have to be made as to what to do in the presence of which files.

## Nice to Have

- [ ] Support for poetry. Need a config file boolean key `use_poetry` or similar which, if True, will make pytoil call poetry in a subprocess if a project contains only a `pyproject.toml` file to create and manage the environment. Because `pyproject.toml` will also exist in pip-managed packages, this should check for anything to do with setuptools (`setup.py`, `setup.cfg` etc.) only falling back to poetry when neither of these are found.
- [ ] Be able to fork a repo? i.e. if a user runs `pytoil checkout someoneelse/repo` pytoil first forks that repo to the users account, clones it, and sets `upstream` to the original repo.
- [ ] Support shell completion for project names regardless of where user is calling pytoil from. I.e. should be able to do `pytoil checkout mypro<TAB>` and pytoil should look in configured projects dir for a match then tab autocomplete that match
