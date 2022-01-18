# Remove

This one is easy! `remove` does exactly what it says. It will recursively delete an entire project from your local projects directory. Since this is quite a destructive action, pytoil will prompt you to confirm before it does anything. If you say no, the entire process will be aborted and your project will be left alone!

!!! warning

    The deletion of a project like this is irreversible. It does not send the folder to Trash, it simply erases it from all existence in the universe, so make sure you know what you're doing before saying yes! :scream:

!!! success "Don't Panic!"

    Don't worry though, `remove` **DOES NOT** go near anything on your GitHub, only your local directories are affected by `remove`. pytoil only makes HTTP GET and POST requests to the GitHub API so you couldn't even delete a repo if you wanted to, in fact you can't make any changes to any GitHub repo with pytoil whatsoever so you're completely safe! :grin:

## Help

<div class="termy">

```console
$ pytoil remove --help

Usage: pytoil remove [OPTIONS] [PROJECTS]...

  Remove projects from your local filesystem.

  The remove command provides an easy interface for decluttering your local
  projects directory.

  You can selectively remove any number of projects by passing them as
  arguments or nuke the whole lot with "--all/-a" if you want.

  As with most programmatic deleting, the directories are deleted instantly
  and not sent to trash. As such, pytoil will prompt you for confirmation
  before doing anything.

  The "--force/-f" flag can be used to force deletion without the confirmation
  prompt. Use with caution!

  Examples:

  $ pytoil remove project1 project2 project3

  $ pytoil remove project1 project2 project3 --force

  $ pytoil remove --all

  $ pytoil remove --all --force

Options:
  -f, --force  Force delete without confirmation.
  -a, --all    Delete all of your local projects.
  --help       Show this message and exit.
```

</div>

## Remove Individual Projects

If you want to remove one or more specific projects, just pass them to `remove` as arguments.

<div class="termy">

```console
$ pytoil remove my_project my_other_project this_one_too

# This will remove my_project, my_other_project, this_one_too from your local filesystem. Are you sure? [y/N]:$ y

Removed: 'my_project'.
Removed: 'my_other_project'.
Removed: 'this_one_too'
```

</div>

And if you say no...

<div class="termy">

```console
$ pytoil remove my_project my_other_project this_one_too

# This will remove my_project, my_other_project, this_one_too from your local filesystem. Are you sure? [y/N]:$ n

Aborted!
```

</div>

## Nuke your Projects Directory

And if you've completely given up and decided you don't want to be a developer anymore (we've all been there), you can erase all your local projects:

<div class="termy">

```console
$ pytoil remove --all

# This will remove ALL your projects. Are you okay? [y/N]:$ y

Removed: 'remove1'.
Removed: 'remove2'.
Removed: 'remove3'.
```

</div>

!!! note

    Because pytoil is written from the ground up to be asynchronous, all the removing happens concurrently in the asyncio event loop so it should
    be nice and snappy even for lots of very large projects! 🚀

## Force Deletion

If you're really sure what you're doing, you can get around the confirmation prompt by using the `--force/-f` flag.

<div class="termy">

```console
$ pytoil remove project1 project2 --force

Removed: 'remove1'.
Removed: 'remove2'.
Removed: 'remove3'.
```

</div>
