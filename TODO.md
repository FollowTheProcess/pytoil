# pytoil's TODO

## Tweaks & Fixes

- [ ] Tweak how `Config` works such that every object/method that needs a `Config` can either have it's required arguments passed in directly into the method, or use the passed in `Config` object. This should eliminate a lot of mocking complexity in the tests and make sure we don't need to keep calling `config.get` everywhere that needs it which is IO expensive.

## Essentials

- [ ] If creating a virtual environment on `checkout` should have some logic to detect the presence of requirements files and automatically install them into the environment. So like `pip install -r requirements.txt` or `pip install -e .[dev]` etc. Some assumptions may have to be made as to what to do in the presence of which files.

## Nice to Have

- [ ] Support for poetry. Need a config file boolean key `use_poetry` or similar which, if True, will make pytoil call poetry in a subprocess if a project contains only a `pyproject.toml` file to create and manage the environment. Because `pyproject.toml` will also exist in pip-managed packages, this should check for anything to do with setuptools (`setup.py`, `setup.cfg` etc.) only falling back to poetry when neither of these are found.
- [ ] Be able to fork a repo?
