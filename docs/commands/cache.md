# Cache

In order to work correctly and show you about your repos on GitHub, pytoil must interact with GitHub. To be precise, it
makes requests to the [GitHub GraphQL API].

However, pytoil does not hit this API **every time** you make a request, it's a bit smarter than that! 🧠

It instead saves responses to the requests it's made to disk, so that the next time you need that information it can quickly pull it from a file rather than reach out over the internet and hit the API again.

This saves you time (particularly if your network connection isn't great) and it saves making many identical requests to the GitHub API (which is always good practice! 👍🏻)

This cache has a default timeout of 120 seconds (which you can tweak if you like, see [config]).

This means that if you invoke a pytoil command that uses the GitHub API, it's response will be cached on disk for 120 seconds.

So if you were to execute that same command at any point in the next 120 seconds, the information you see will be from the cache, **not** from the GitHub API.

The cache is absolutely tiny and is totally self-managing so 99% of the time you won't have to worry about it, it simply does it's job in the background for you!

However, sometimes you might want to ensure you get the most up to date response, just want to clear the whole cache, or maybe ensure that the cache itself contains the most up to date data.

This is where the `pytoil cache` subcommand comes in!

!!! note

    The pytoil commands that make use of these cached responses are:

    * `show remote`
    * `show diff`
    * `show forks`
    * `find`

## Help

[GitHub GraphQL API]: https://docs.github.com/en/graphql
[config]: ../config.md

<div class="termy">

```console
$ pytoil cache --help

Usage: pytoil cache [OPTIONS] COMMAND [ARGS]...

  Interact with pytoil's cache.

  Pytoil caches the responses from the GitHub API so that it doesn't have to
  hit it so often and so a user gets the snappiest experience possible using
  the CLI.

  The cache subcommand allows you to interact with this cache, either forcing
  a manual refresh or flushing it entirely.

Options:
  --help  Show this message and exit.

Commands:
  clear    Clear pytoil's cache.
  refresh  Force a manual refresh of the cache.
```

</div>

As you can see, the `pytoil cache` subcommand group has two commands: `clear` and `refresh`.

## Clear

Clear does one thing. It simply removes the entire cache directory from disk, ensuring that the next API call will come directly from GitHub and a brand new cache will be created.

<div class="termy">

```console
$ pytoil cache clear

✔ Cache cleared successfully

```

</div>

!!! tip

    You'd use `clear` if you wanted the next request you made to have the most up to date information in it.

## Refresh

The other command, `refresh` does two things!

* Clears the cache completely
* Calls every API endpoint pytoil knows about concurrently to re-populate the cache with the latest data

<div class="termy">

```console
$ pytoil cache refresh

✔ Cache refreshed successfully
```

</div>

!!! tip

    You'd use `refresh` if you wanted to guarantee that the cache contained the most up to date data in it.
