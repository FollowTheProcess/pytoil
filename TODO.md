# Pytoil TODO

Ideas for enhancements or fixes.

## Enhancements

- [ ] When batch pulling repos, do it in parallel? Wouldn't need threads or anything like that, just a series of calls to `subprocess.Popen` which spawns a subprocess but does not wait for it to complete like `subprocess.run` does. Therefore we could fire off all the `git clones` for each url and just report when they're all done. Probably have to do it in some sort of task queue with workers though incase someone has thousands of repos and it bricks the machine!
- [ ] On `pytoil new --starter --venv` make it export a `requirement.txt` or `environment.yml`
- [ ] If the repo passed to `pytoil checkout` is of the form `username/repo`, pytoil will first fork that repo to the user, then clone it as normal. This means pytoil can now be used to easily collaborate on open source stuff.
- [ ] Automatically detect requirements. E.g. if project is checked out with `--venv` pytoil should look for things like `requirements.txt`, `requirements_dev.txt`, `setup.cfg`, `pyproject.toml` etc and see if it can parse requirements and install them.

## Fixes

## Roadmap

- Currently the CLI itself is not tested (other than manually). This is intentional as when I previously tested the CLI it became very complex and coupled and made making CLI changes very difficult. As the CLI gets solidified, these automated tests will come back. The core logic of `pytoil` has 100% test coverage.

## Automatically Installing Requirements

I think the best way to do this is to add `Flit` and `Poetry` environments all subclassing from `Environment`. Then add an `install_self` method which will do the appropriate thing:

- For setuptools and pip it will look for `requirements_dev.txt`, `requirements.txt` first in the case we've checked out, not a package but a project. Then if neither of those it will just do `pip install -e .[dev]` assuming we've checked out a package.

- For flit it will make a standard python environment as normal, then the `install_self` method will run something like `flit install --deps develop --symlink --python {python_path}` which is flit's equivalent of a development install

- For poetry it will just delegate to poetry for everything. I.e. `create` will just run `poetry install` which should take care of everything.

- Conda already has this in `create_from_yml`. Which reminds me actually: this isn't currently hooked up to the CLI. On checkout we just call `create` which makes a fresh environment. Look into this!
