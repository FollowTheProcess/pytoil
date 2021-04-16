# Info

Another easy one! `info` simply shows you some summary information about whatever project you tell it to.

<div class="termy">

```console
// Let's get some info about pytoil
$ pytoil info pytoil

Info for: pytoil

name: pytoil
description: CLI to automate the development workflow.
created_at: 2021-02-04T15:05:23Z
updated_at: 2021-03-02T11:09:08Z
size: 219
license: Apache License 2.0
remote: True
local: True
```

</div>

What happens here is pytoil uses the GitHub personal access token we talked about in [config] and hits the GitHub API to find out some basic information about the repo you pass to it :white_check_mark:

pytoil will always prefer this way of doing it as we can get things like license information and description which is a bit more helpful to show. If however, the project you're asking for information about does not exist on GitHub yet, you'll still get some info back!

<div class="termy">

```console
// Some project thats not on GitHub yet
$ pytoil info my_local_project

Info for: my_local_project

name: my_local_project
created_at: 2021-02-27 12:37:18
updated_at: 2021-02-27 12:48:18
size: 256
local: True
remote: False
```

</div>

!!! note

    pytoil grabs this data from your operating system by using the `Path.stat()` method from [pathlib] :computer:

[config]: ../config.md
[pathlib]: https://docs.python.org/3/library/pathlib.html
