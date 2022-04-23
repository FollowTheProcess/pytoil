# Config

The `config` subcommand is pytoil's programmatic access to it's own configuration file! Here you can get, show and get help about the configuration.

## Help

<div class="termy">

```console
$ pytoil config --help

Usage: pytoil config [OPTIONS] COMMAND [ARGS]...

  Interact with pytoil's configuration.

  The config command group allows you to get, show and explain pytoil's
  configuration.

Options:
  --help  Show this message and exit.

Commands:
  edit     Open pytoil's config file in $EDITOR.
  explain  Print a list and description of pytoil config values.
  get      Get the currently set value for a config key.
  show     Show pytoil's config.
```

</div>

## Get

`get` does what it says. It gets a valid config key-value pair from your file and shows it to you. Simple!

<div class="termy">

```console
$ pytoil config get editor

editor: code-insiders
```

</div>

## Show

`show` is just a handy way of seeing what the current config is without having to go to the config file!

<div class="termy">

```console
$ pytoil config show

               Key   Value
 ─────────────────────────────────────────────────────────────
     projects_dir:   /Users/tomfleet/Development
            token:   skjdbakshbv82v27676cv
         username:   FollowTheProcess
           editor:   code-insiders
        conda_bin:   mamba
  common_packages:   ['black', 'mypy', 'isort', 'flake8']
              git:   True

```

</div>

## Edit

`edit` simply opens up the pytoil config file in your $EDITOR so you can make any changes you like!

<div class="termy">

```console
$pytoil config edit

Opening ~/.pytoil.toml in your $EDITOR
```

</div>

## Explain

The command `pytoil config explain` outputs a (hopefully) helpful description of the pytoil configuration schema.

[pydantic]: https://pydantic-docs.helpmanual.io
