# Remove

This one is easy! `remove` does exactly what it says. It will recursively delete an entire project from your local projects directory. Since this is quite a destructive action, pytoil will prompt you to confirm before it does anything. If you say no, the entire process will be aborted and your project will be left alone!

!!! warning

    The deletion of a project like this is irreversible. It does not send the folder to Trash, it simply erases it from all existence in the universe, so make sure you know what you're doing before saying yes! :scream:

!!! success "Don't Panic!"

    Don't worry though, `remove` **DOES NOT** go near anything on your GitHub, only your local directories are affected by `remove`. pytoil only makes HTTP GET requests to the GitHub API so you couldn't even delete a repo if you wanted to, in fact you can't make any changes to any GitHub repo with pytoil whatsoever so you're completely safe! :grin:

## Remove Single Project

<div class="termy">

```console
$ pytoil remove my_project

# This will remove ['my_project'] from your local filesystem. Are you sure? [y/N]:$ y

Removing project: 'my_project'.

Done!
```

</div>

And if you say no...

<div class="termy">

```console
$ pytoil remove my_project

# This will remove ['my_project'] from your local filesystem. Are you sure? [y/N]:$ n

Aborted!
```

</div>

## Remove Multiple Projects

`remove` also accepts a list of projects if you want to remove a few in one go:

<div class="termy">

```console
$ pytoil remove remove1 remove2 remove3

# This will remove ['remove1', 'remove2', 'remove3'] from your local filesystem. Are you sure? [y/N]:$ y

Removing project: 'remove1'.
Removing project: 'remove2'.
Removing project: 'remove3'.

Done!
```

</div>

## Nuke your Projects Directory

And if you've completely given up and decided you don't want to be a developer anymore (we've all been there), you can erase all your local projects:

<div class="termy">

```console
$ pytoil remove --all

# This will remove all your projects. Are you okay? [y/N]:$ y

Removing project: 'remove1'.
Removing project: 'remove2'.
Removing project: 'remove3'.

Done!
```

</div>
