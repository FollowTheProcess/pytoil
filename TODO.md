# TODO

- [ ] VirtualEnv.install should also take a requirements file which it passes to `pip install -r {file}`. This argument should be mutually exclusive to all other arguments.
- [ ] Detecting whether a project should use virtualenv/pip/requirements.txt or conda or a PEP517 compatible virtualenv/pip or something else like poetry/flit etc.

## Optional

- [ ] VSCode specific stuff like setting `python.pythonPath` and `python.testing.pytestEnabled`

## Detecting which environment

**If `setup.py` and/or `setup.cfg` but no `pyproject.toml`:**

- Project must be a pip project that uses setuptools but is not PEP517/518 compliant
- Probably also has a `requirements.txt` or `requirements_dev.txt` etc.
- Use `virtualenv`
- Could support prefixes like `.[dev]`
- Only supports editable installs if there is a `setup.py`

**If above but this time with a `pyproject.toml`:**

- Project still uses pip/setuptools but this time it is PEP517/518 compliant
- This means no `requirements.txt` it's likely all in `setup.py` or `setup.cfg`
- Use `virtualenv`
- Could support prexises like `.[dev]`
- Only supports editable installs if there is a `setup.py`

**If just `pyproject.toml`:**

- Project does not use pip/setuptools but instead relies on an alternative build system (via PEP517/518)
- This is likely to be Flit or Poetry
- Determining which will require parsing the `pyproject.toml`
- If flit: use `virtualenv` as normal
- If poetry: poetry will manage everything

**If `environment.yml`:**

- Conda is easy. If it has an `environment.yml` it is a conda environment.
