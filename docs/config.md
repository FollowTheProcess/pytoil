# Config

There's really not much to configure, all pytoil needs to know about is:

* Where you keep your projects (`projects_dir`)
* What your GitHub username is (`username`)
* Your GitHub personal access token (`token`)
* Whether you want pytoil to open things in VSCode (`vscode`)

If you don't know how to generate a GitHub token, check out the [docs].

!!! info

    Don't worry about giving pytoil your personal token. All we do with it is make HTTP GET requests to the GitHub
    API using your token to authenticate the requests so we can tell which repos you have on GitHub and some very basic information about them.

    In fact, the only permissions pytoil needs is read repo access! :smiley:

!!! note

    I used VSCode as the only configurable editor as it's the one I use and is therefore the only one I have experience with configuring programmatically and launching via the command line.

    If you want to help add support for more editors then PR's are always welcome!

## The Config File

After you install pytoil, you should run the following command and follow the prompts

<div class="termy">

```console
$ pytoil init

# GitHub username:$ YourGitHubUsername
# GitHub personal access token:$ YourTokenHere
# Absolute path to your projects directory:$ /Users/you/projects
# Use VSCode to open projects with?:$ True
```

</div>

pytoil will then will write that config to a file: `~/.pytoil.yml`.

!!! note

    You only need to run this command once on initial setup (or if you delete the config file). After that your config is saved.

You could always just edit the file manually if you like, it will look like this:

```yaml
# ~/.pytoil.yml

username: "FollowTheProcess"
projects_dir: "/Users/me/projects"
token: "thisismygithubtoken"
vscode: True
```

!!! warning

    The only thing that might trip you up is that `projects_dir` must be the **absolute** path to where you keep your projects. So you'll need to explicitly state the entire path (as in the example above) starting from the root.

## Control using pytoil

Of course, even after you've run `pytoil init` you can still easily get and set the config through the `pytoil config` subcommand.

### View Current Config

<div class="termy">

```console
$ pytoil config show

Current pytoil config:

username: 'YourUsername'
token: 'YourToken'
projects_dir: '/Users/you/projects'
vscode: True
```

</div>

### Set a Config Value

<div class="termy">

```console
$ pytoil config set username mynewusername

Configuration updated: 'username' is now 'mynewusername'.
```

</div>

[docs]: https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
