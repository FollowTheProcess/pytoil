# Show

We've seen a hint at some pytoil commands but lets dive in properly.

Let's look at how you can use pytoil to help *you* :thumbsup:

The first subcommand we will look at is `pytoil show`.

`show` does what it says on the tin and provides a nice way of showing your local and remote projects.

!!! note

    `show` always shows the projects in alphabetical order :abc:

Let's start with the help...

## Help

<div class="termy">

```console
$ pytoil show --help

Usage: pytoil show [OPTIONS] COMMAND [ARGS]...

  View your local/remote projects.

  The show command provides an easy way of listing of the projects you have
  locally in your configured development directory and/or of those you have on
  GitHub (known in pytoil-land as 'remote' projects).

  Local projects will be the names of subdirectories in your configured
  projects directory.

  The remote projects listed here will be those owned by you on GitHub.

  The "--limit/-l" flag can be used if you only want to see a certain number
  of results.

Options:
  --help  Show this message and exit.

Commands:
  diff    Show the difference in local/remote projects.
  forks   Show your forked projects.
  local   Show your local projects.
  remote  Show your remote projects.
```

</div>

!!! tip

    Remember, each subcommand has its own help you can check out too. e.g. `pytoil show local --help` :thumbsup:

## Local

`local` shows all the projects you already have in your configured projects directory (see [config] for how to set this!). If you don't have any local projects yet, pytoil will let you know.

<div class="termy">

```console
$ pytoil show local
Local Projects

Showing 3 out of 3 local projects

  Name              Created          Modified
 ───────────────────────────────────────────────────
  project 1         13 days ago      9 days ago
  project 2         a day ago        a minute ago
  project 3         a month ago      a month ago
```

</div>

## Remote

`remote` shows all the projects on your GitHub (you may or may not have some of these locally too). If you don't have any remote projects yet, pytoil will let you know.

<div class="termy">

```console
$ pytoil show remote
Remote Projects

Showing 5 out of 31 remote projects

  Name                  Size       Created                Modified
 ───────────────────────────────────────────────────────────────────────
  advent_of_code_2020   46.1 kB    12 days ago            9 days ago
  advent_of_code_2021   154.6 kB   a month ago            29 days ago
  aircraft_crashes      2.1 MB     1 year, 15 days ago    11 months ago
  cookie_pypackage      753.7 kB   1 year, 6 months ago   a month ago
  cv                    148.5 kB   2 months ago           7 days ago

```

</div>

[config]: ../config.md

## Diff

`diff` shows all the projects you have on GitHub, but don't yet exist locally. If your local projects folder has all your GitHub projects in it, pytoil will let you know this too.

<div class="termy">

```console
$ pytoil show diff
Diff: Remote - Local

Showing 5 out of 26 projects

  Name                  Size       Created                Modified
 ─────────────────────────────────────────────────────────────────────────────
  advent_of_code_2021   154.6 kB   a month ago            29 days ago
  aircraft_crashes      2.1 MB     1 year, 15 days ago    11 months ago
  cookie_pypackage      753.7 kB   1 year, 6 months ago   a month ago
  cv                    148.5 kB   2 months ago           7 days ago
  eu_energy_analysis    1.9 MB     1 year, 1 month ago    1 year, 25 days ago

```

</div>

## Forks

You can also see all your forked repos and whether or not they are available locally!

<div class="termy">

```console
$ pytoil show forks
Forked Projects

Showing 2 out of 2 forked projects

  Name              Size       Forked         Modified       Parent
 ────────────────────────────────────────────────────────────────────────────────────────
  nox               5.2 MB     6 months ago   10 days ago    theacodes/nox
  python-launcher   843.8 kB   2 months ago   2 months ago   brettcannon/python-launcher

```

</div>

[config]: ../config.md
