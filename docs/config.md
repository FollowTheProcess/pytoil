# Config

There's really not much to configure, all pytoil needs to know about is:

* Where you keep your projects (`projects_dir`)
* What your GitHub username is (`username`)
* And your GitHub personal access token (`token`)

If you don't know how to generate a GitHub token, check out the [docs].

!!! info

    Don't worry about giving pytoil your personal token. All we do with it is make http GET requests to the GitHub
    API using your token to authenticate the requests so we can tell which repos you have on GitHub and some very basic information about them.

    In fact, the only permissions pytoil needs is read repo access! :smiley:

## The Config File

After you install pytoil, you should run the following command.

```shell
pytoil init
```

This will interactively prompt you to enter the required config and then will write that config to a file `~/.pytoil.yml`.

You only need to run this command once on initial setup (or if you delete the config file). After that your config is saved.

You could always just edit the file manually if you like, it will look like this:

```yaml
# ~/.pytoil.yml

username: "FollowTheProcess"
projects_dir: "/Users/me/projects"
token: "thisismygithubtoken"
```

!!! warning

    The only thing that might trip you up is that `projects_dir` must be the **absolute** path to where you keep your projects. So you'll need to explicitly state the entire path (as in the example above) starting from the root.

## Control using pytoil

Of course, even after you've run `pytoil init` you can still easily get and set the config through the `pytoil config` subcommand.

Like so:

```shell
pytoil config show
```

[docs]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
