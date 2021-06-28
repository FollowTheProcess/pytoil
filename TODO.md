# Pytoil TODO

Ideas for enhancements or fixes.

## Enhancements

- [ ] When batch pulling repos, do it in parallel? Wouldn't need threads or anything like that, just a series of calls to `subprocess.Popen` which spawns a subprocess but does not wait for it to complete like `subprocess.run` does. Therefore we could fire off all the `git clones` for each url and just report when they're all done. Probably have to do it in some sort of task queue with workers though incase someone has thousands of repos and it bricks the machine!
- [ ] On `pytoil new --starter --venv` make it export a `requirement.txt` or `environment.yml`
- [x] Add a `--count` option to `pytoil show` subcommands where it just gives you the count. On `diff` and `all` this should tell you the % of projects you have locally and remotely.

## Fixes
