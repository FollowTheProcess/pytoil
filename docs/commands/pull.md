# Pull

`pull` does exactly what it sounds like, it provides a nice easy way to pull down multiple projects at once and saves you having to type `git clone` like a million times :sleeping:

Any projects you already have locally will be completely skipped by `pull` so it's impossible to overwrite any local changes to projects :white_check_mark:

## Help

<div class="termy">

```console
$ pytoil pull --help

Usage: pytoil pull [OPTIONS] [PROJECTS]...

  Pull down your remote projects.

  The pull command provides easy methods for pulling down remote projects.

  It is effectively a nice wrapper around git clone but you don't have to
  worry about urls or what your cwd is, pull will grab your remote projects by
  name and clone them to your configured projects directory.

  You can also use pull to batch clone multiple repos, even all of them ("--
  all/-a") if you're into that sorta thing.

  If more than 1 repo is passed (or if "--all/-a" is used) pytoil will pull
  the repos concurrently, speeding up the process.

  Any remote project that already exists locally will be skipped and none of
  your local projects are changed in any way. pytoil will only pull down those
  projects that don't already exist locally.

  It's very possible to accidentally clone a lot of repos when using pull so
  you will be prompted for confirmation before pytoil does anything.

  The "--force/-f" flag can be used to override this confirmation prompt if
  desired.

  Examples:

  $ pytoil pull project1 project2 project3

  $ pytoil pull project1 project2 project3 --force

  $ pytoil pull --all

  $ pytoil pull --all --force

Options:
  -f, --force  Force pull without confirmation.
  -a, --all    Pull down all your projects.
  --help       Show this message and exit.
```

</div>

## All

When you run `pytoil pull --all` pytoil will scan your projects directory and your GitHub repos to calculate what's missing locally and then go and grab the required repos concurrently so it's as fast as possible (useful if you have a lot of repos!) :dash:

<div class="termy">

```console
$ pytoil pull --all

# This will clone 7 repos. Are you sure you wish to proceed? [y/N]:$ y

Cloned 'repo1'...

Cloned 'repo2'...

etc...
```

</div>

!!! warning

    Even though this is done concurrently, if you have lots of GitHub repos (> 50 or so) this could still take a few seconds, you might be better off selecting specific repos to pull by using `pytoil pull [project(s)]`. More on that down here :point_down:

    However, it will prompt you telling you exactly how many repos it is going to clone and ask you to confirm! This confirmation can be disabled by using the `--force/-f` flag.

<div class="termy">

```console
$ pytoil pull --all

# This will clone 1375 repos. Are you sure you wish to proceed? [y/N]:$ n

// Lol... nope!

Aborted!
```

</div>

## Some

If you have a lot of repos or you only want a few of them, `pytoil pull` accepts a space separated list of projects as arguments.

Doing it this way, it will again check if you already have any of these locally (and skip them if you do) and finally do the cloning. Like so:

<div class="termy">

```console
$ pytoil pull repo1 repo2 repo3 cloned1

// In this snippet, our user already has 'cloned1' locally so it's skipped

# This will clone 3 repos. Are you sure you wish to proceed? [y/N]:$ y

Cloning 'repo1'...

Cloning 'repo2'...

etc...
```

</div>

And just like `--all` you can abort the whole operation by entering `n` when prompted.

<div class="termy">

```console
$ pytoil pull repo1 repo2 repo3 cloned1

// In this snippet, our user already has 'cloned1' locally so it's skipped

# This will clone 3 repos. Are you sure you wish to proceed? [y/N]:$ n

Aborted!
```

</div>

!!! note

    If you pass more than 1 repo as an argument, it will also be cloned concurrently :dash:
