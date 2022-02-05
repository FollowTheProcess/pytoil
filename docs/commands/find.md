# Find

The `find` command lets you easily search for one of your projects (even if you can't exactly remember it's name 🤔).

## Help

<div class="termy">

```console
$ pytoil find --help

Usage: pytoil find [OPTIONS] PROJECT

  Quickly locate a project.

  The find command provides a fuzzy search for finding a project when you
  don't know where it is (local or on GitHub).

  It will perform a fuzzy search through all your local and remote projects,
  bring back the best matches and show you where they are.

  Useful if you have a lot of projects and you can't quite remember what the
  one you want is called!

  The "-l/--limit" flag can be used to alter the number of returned search
  results, but bare in mind that matches with sufficient match score are
  returned anyway so the results flag only limits the maximum number of
  results shown.

  Examples:

  $ pytoil find my

  $ pytoil find proj --limit 5

Options:
  -l, --limit INTEGER  Limit results to maximum number.  [default: 5]
  --help               Show this message and exit.
```

</div>

## Searching for Projects

<div class="termy">

```console
// I swear it was called python... something
$ pytoil find python


  Project           Similarity   Where
 ───────────────────────────────────────
  py                90           Remote
  python-launcher   90           Remote

```

</div>

What pytoil does here is it takes the argument you give it, fetches all your projects and does a fuzzy text match against
all of them, wittles down the best matches and shows them to you (along with whether they are available locally or on GitHub).

Isn't that useful! 🎉

!!! info

    Under the hood, pytoil uses the excellent [thefuzz] library to do this, which implements the [Levenshtein distance]
    algorithm to find the best matches 🚀

## 404 - Project Not Found

If `find` can't find a match in any of your projects, you'll get a helpful warning...

<div class="termy">

```console
// Something that won't match
$ pytoil find dingledangledongle

⚠ No matches found!
```

</div>

[thefuzz]: https://github.com/seatgeek/thefuzz
[Levenshtein distance]: https://en.wikipedia.org/wiki/Levenshtein_distance
