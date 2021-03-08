# TODO

Things are getting a bit messy and hard to change so I think I need a clean up.

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
