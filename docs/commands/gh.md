# gh

Sometimes you just want to quickly go to the GitHub page for your project. Enter the incredibly simple `gh` command!

<div class="termy">

```console
$ pytoil gh my_project

Opening 'my_project' in your browser...

// Now you're at the GitHub page for the project!
```

</div>

## PR's and Issues

`gh` provides two flags to immediately open the pull requests or issues section of the specified repo. Knock yourself out!

<div class="termy">

```console
$ pytoil gh my_project --help

Usage: pytoil gh [OPTIONS] PROJECT

  Open one of your projects on GitHub.

  Given a project name (must exist on GitHub and be owned by you), 'gh' will
  open your browser and navigate to the project on GitHub.

  You can also use the "--issues" or "--prs" flags to immediately open up the
  repo's issues or pull requests page.

  Examples:

  $ pytoil gh my_project

  $ pytoil gh my_project --issues

  $ pytoil gh my_project --prs

Options:
  -i, --issues  Go to the issues page.
  -p, --prs     Go to the pull requests page.
  --help        Show this message and exit.
```

</div>
