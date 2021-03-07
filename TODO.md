# TODO

Things are getting a bit messy and hard to change so I think I need a clean up.

## Make an ABC for Virtual Environment

Define an abstract base class to be inherited by both VirtualEnv and CondaEnv.

Should have:

### Property: Path

Since virtual environments are so closely tied to specific projects. It makes sense to have a `path` which is the root of the linked project.

`VirtualEnv` already does this because it has to know where to put the `.venv` but conda doesn't and not having it is making things a mess.

### Property: Executable

A `pathlib.Path` pointing to that venv's python. This should always be `None` except if and only if the environment exists and is otherwise valid.

This means that if `env.executable` it not `None`, you can just use it and it will work.

This also comes in handy for setting VSCode python path.

### Method: Exists

A method of checking whether or not the environment already exists. For a virtualenv this will just look if a `.venv` directory exists in the root project path.

Conda parses the return from `conda env list` but if we now know which conda a user has installed (anaconda/miniconda), we can just look in the ~/miniconda3/envs directory for example looking for a directory with the matching name. This is probably much faster than waiting for `conda env list`.

In fact, we could just do `self.path.exists()`? If it has an interpreter under the correct path, it must exist no?

### Method: Raise for Executable

Based on the boolean return from `.exists()` but will raise an exception if an interpreter is not found.

### Method: Create

A method to create the environment from scratch.

### Method: Install

Method to install packages into the chosen environemnt.

CondaEnv would just call `conda install --name...`.

VirtualEnv just uses `self.executable` to invoke `pip`.

## Switch to Cleo for the CLI?

Typer is great but as the command complexity grows I find it gets a bit messy. Something more composable and object oriented like Cleo might work nicely.

Each command in cleo is a class and the method `handle` does all the work. But crucially, you can add other methods that belong to that class to abstract away some of the logic.

I like the API of the CLI, so keep that the same I think it works well.

## Clean way to detect what environment a project is

This is the main thing I want this tool to do.

Based on what files the project contains, dispatch to the correct environment.

With the new ABC approach this could be something like:

```python
def env_dispatcher(project: pathlib.Path) -> VirtualEnvABC: # Or whatever its called
    if project.is_conda():
        # Return a CondaEnv object
    elif project.is_virtualenv():
        # Return a VirtualEnv object
    else:
        # Raise or warn or whatever
```

Then using this elsewhere in the project would be like:

```python
project_env = env_dispatcher(project=my_conda_project)
# So now project_env is a CondaEnv
project_env.create()
```

This would work exactly the same if the project was a virtualenv one, because of the ABC. This means you could do this upfront and the syntax to create, install, whatever the environment would be identical in the CLI command:

```python
def checkout(project):

    # Get the environment
    project_env = env_dispatcher(project)

    # Syntax for setting up the project is identical
    project_env.create()
    project_env.install(["stuff"])
```

## Other Tweaks and Tidies

* `CondaEnv.create_from_yml` should take the project root, not the path to the `environment.yml` this is a pain to enter and `environment.yml` is in the project root 99%+ of the time.
* It should also return a `CondaEnv` object, not `None` i.e. make it a `classmethod`.
