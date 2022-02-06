# Keep

`keep` is effectively the opposite of [remove], it deletes everything **except** the projects you specify from your local projects directory.

It is useful when you want to declutter your projects directory but don't want to pass lots of arguments to [remove], with `keep` you can tell pytoil the projects you want to keep, and it will remove everything else for you!

## Help

<div class="termy">

```console
$ pytoil keep --help

Usage: pytoil keep [OPTIONS] [PROJECTS]...

  Remove all but the specified projects.

  The keep command lets you delete all projects from your local projects
  directory whilst keeping the specified ones untouched.

  It is effectively the inverse of `pytoil remove`.

  As with most programmatic deleting, the directories are deleted instantly
  and not sent to trash. As such, pytoil will prompt you for confirmation
  before doing anything.

  The "--force/-f" flag can be used to force deletion without the confirmation
  prompt. Use with caution!

  Examples:

  $ pytoil keep project1 project2 project3

  $ pytoil keep project1 project2 project3 --force

Options:
  -f, --force  Force delete without confirmation.
  --help       Show this message and exit.
```

</div>

[remove]: ./remove.md

## Usage

To use `keep` just pass the projects you want to keep as arguments.

<div class="termy">

```console
$ pytoil keep project other_project another_project

# This will delete remove1, remove2, remove3 from your local filesystem. Are you sure? [y/N]:$ y

Deleted: remove1.
Deleted: remove2.
Deleted: remove3.
```

</div>

And if you say no...

<div class="termy">

```console
$ pytoil keep project other_project another_project

# This will delete remove1, remove2, remove3 from your local filesystem. Are you sure? [y/N]:$ n

Aborted!
```

</div>

## Force Deletion

If you're really sure what you're doing, you can get around the confirmation prompt by using the `--force/-f` flag.

<div class="termy">

```console
$ pytoil keep project1 project2 --force

Removed: remove1.
Removed: remove2.
Removed: remove3.
```

</div>
