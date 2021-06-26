# Pytoil TODO

Ideas for enhancements or fixes.

## Enhancements

- [ ] When batch pulling repos, do it in parallel? Wouldn't need threads or anything like that, just a series of calls to `subprocess.Popen` which spawns a subprocess but does not wait for it to complete like `subprocess.run` does. Therefore we could fire off all the `git clones` for each url and just report when they're all done.

## Fixes
