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
  locally in your configured development directory and/or of those you have
  on GitHub (known in pytoil-land as 'remote' projects).

  Local projects will be the names of subdirectories in your configured
  projects directory.

  The remote projects listed here will be those owned by you on GitHub.

Options:
  --help  Show this message and exit.

Commands:
  all     Show all your projects, grouped by local and remote.
  diff    Show the difference in local/remote projects.
  local   Show your local projects.
  remote  Show your remote projects.

```

</div>

!!! tip

    Remember, each subcommand has its own help you can check out too. e.g. `pytoil show local --help` :thumbsup:

## All

`all` will show you... well *all* of your projects, separated by whether they are local (already available on your computer) or remote (on your GitHub, may or may not also be local).

<div class="termy">

```console
$ pytoil show all

Local Projects:

- Local1
- Local2
- Local3
- Cloned1
- Cloned2

Remote Projects:

- Cloned1
- Cloned2
- Remote1
```

</div>

!!! note

    In this snippet, the user has already cloned `Cloned1` and `Cloned2` so they show up in both sections. If you want to only show remote projects that you don't have locally, you need the `diff` command. Keep scrolling :point_down:

## Local

`local` shows all the projects you already have in your configured projects directory (see [config] for how to set this!). If you don't have any local projects yet, pytoil will let you know.

<div class="termy">

```console
$ pytoil show local

Local Projects:

- Local1
- Local2
- Local3
- Cloned1
- Cloned2
```

</div>

## Remote

`remote` shows all the projects on your GitHub (you may or may not have some of these locally too). If you don't have any remote projects yet, pytoil will let you know.

<div class="termy">

```console
$ pytoil show remote

Remote Projects:

- Cloned1
- Cloned2
- Remote1
```

</div>

[config]: ../config.md

## Diff

`diff` shows all the projects you have on GitHub, but don't yet exist locally. If your local projects folder has all your GitHub projects in it, pytoil will let you know this too.

<div class="termy">

```console
$ pytoil show diff

Diff: Remote - Local

- Remote1
- etc...
```

</div>
