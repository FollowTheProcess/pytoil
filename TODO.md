# Pytoil TODO

Ideas for enhancements or fixes.

## Enhancements

- [ ] When batch pulling repos, do it in parallel? Wouldn't need threads or anything like that, just a series of calls to `subprocess.Popen` which spawns a subprocess but does not wait for it to complete like `subprocess.run` does. Therefore we could fire off all the `git clones` for each url and just report when they're all done. Probably have to do it in some sort of task queue with workers though incase someone has thousands of repos and it bricks the machine!
- [ ] On `pytoil new --starter --venv` make it export a `requirement.txt` or `environment.yml`
- [ ] If the repo passed to `pytoil checkout` is of the form `username/repo`, pytoil will first fork that repo to the user, then clone it as normal. This means pytoil can now be used to easily collaborate on open source stuff.

## Fixes

## Roadmap

- Currently the CLI itself is not tested (other than manually). This is intentional as when I previously tested the CLI it became very complex and coupled and made making CLI changes very difficult. As the CLI gets solidified, these automated tests will come back. The core logic of `pytoil` has 100% test coverage.
