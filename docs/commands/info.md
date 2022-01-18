# Info

Another easy one! `info` simply shows you some summary information about whatever project you tell it to.

<div class="termy">

```console
// Let's get some info about pytoil
$ pytoil info pytoil

Info for pytoil:

           Key   Value
 ────────────────────────────────────────────────────────────
         Name:   pytoil
  Description:   CLI to automate the development workflow 🤖
      Created:   11 months ago
      Updated:   7 days ago
         Size:   6.4 MB
      License:   Apache License 2.0
       Remote:   True
        Local:   True

```

</div>

What happens here is pytoil uses the GitHub personal access token we talked about in [config] and hits the GitHub API to find out some basic information about the repo you pass to it :white_check_mark:

pytoil will always prefer this way of doing it as we can get things like license information and description which is a bit more helpful to show. If however, the project you're asking for information about does not exist on GitHub yet, you'll still get some info back!

<div class="termy">

```console
// Some project that's not on GitHub yet
$ pytoil info my_local_project

Info for testy:

       Key   Value
 ───────────────────────────
     Name:   testy
  Created:   23 seconds ago
  Updated:   23 seconds ago
    Local:   True
   Remote:   False

```

</div>

!!! note

    pytoil grabs this data from your operating system by using the `Path.stat()` method from [pathlib] :computer:

[config]: ../config.md
[pathlib]: https://docs.python.org/3/library/pathlib.html
