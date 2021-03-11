# Sync

`sync` does exactly what it sounds like, it provides a nice easy way to pull down multiple projects at once and saves you having to type `git clone` like a million times :sleeping:

Any projects you already have locally will be completely skipped by `sync` so it's impossible to overwrite any local changes to projects :white_check_mark:

## Help

<div class="termy">

```console
$ pytoil sync --help

Usage: pytoil sync [OPTIONS] COMMAND [ARGS]...

  Synchronise your local and remote projects.

  sync is a safe method in that existing local projects will not be modified
  in any way.

Options:
  --help  Show this message and exit.

Commands:
  all    Pull down all your remote projects that aren't already local.
  these  Only pull down specified remote projects.
```

</div>

## All

When you run `pytoil sync all` pytoil will scan your projects directory and your GitHub repos to calculate what's missing locally and then go and grab the missing projects from GitHub one by one.

<div class="termy">

```console
$ pytoil sync all

# This will clone 7 repos. Are you sure you wish to proceed? [y/N]:$ y

Cloning 'repo1'...

Cloning 'repo2'...

etc...
```

</div>

!!! warning

    If you have lots of GitHub repos this could take a while, you might be better off selecting specific repos to sync by using `pytoil sync these`. More on that down here :point_down:

    However, it will prompt you telling you exactly how many repos it is going to clone and ask you to confirm! This confirmation can be disabled by using the `--force/-f` flag.

<div class="termy">

```console
$ pytoil sync all

// This person has a LOT of repos

# This will clone 1375 repos. Are you sure you wish to proceed? [y/N]:$ n

Aborted!
```

</div>

## These

If you have a lot of repos or you only want a few of them, `pytoil sync these` is what you want!

`these` accepts a space-separated list of repo names as an argument and it will again check if you already have any of these locally (and skip them if you do) and finally do the cloning. Like so:

<div class="termy">

```console
$ pytoil sync these repo1 repo2 repo3 cloned1

// In this snippet, our user already has 'cloned1' locally so it's skipped

# This will clone 3 repos. Are you sure you wish to proceed? [y/N]:$ y

Cloning 'repo1'...

Cloning 'repo2'...

etc...
```

</div>

And just like `all` you can abort the whole operation by entering `n` when prompted.

<div class="termy">

```console
$ pytoil sync these repo1 repo2 repo3 cloned1

// In this snippet, our user already has 'cloned1' locally so it's skipped

# This will clone 3 repos. Are you sure you wish to proceed? [y/N]:$ n

Aborted!
```

</div>
