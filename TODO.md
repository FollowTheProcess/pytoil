# Pytoil TODO

Ideas for enhancements or fixes.

## Enhancements

- [ ] When batch pulling repos, do it in parallel?
- [x] Add a `--type` or `--lang` or something to `pytoil new` which points to an `Enum` of languages with a basic starter template implemented. This would then act like `cargo new` or `poetry new` and set up a basic structure. For rust it's probably best to call `cargo new` in a subprocess, for go it should create a basic structure and then run `go mod init`. For python I think we'll just have to do std lib stuff to keep it universal. Or maybe have a `flit`, `poetry`, `std` enum or something
- [ ] Remove and pull should be able to accept bare args as typing remove these is counter intuitive.

## Fixes
