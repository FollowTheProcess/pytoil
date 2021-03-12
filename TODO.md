# TODO

Below are a list of enhancements or fixes discovered during pre-release testing:

## Immediate Fixes

- [x] Setting python path in vscode settings errors if file is missing or it's empty
- [ ] Ensure all examples in help say "Examples" not "Example"
- [ ] Pytoil config show raises ugly error when config file doesn't exist
- [ ] Same with config set
- [ ] Add clarifying message to pytoil init when config file already exists saying it's checking or something
- [ ] Make pytoil init check more robust than just whether or not the file exists. See if it has the right keys etc. Or even just a check that it's not empty.
- [ ] "Removing project: project" should be yellow maybe?
- [ ] Creating a new conda project when the environment already exists raises an ugly error. Should instead just set the python path in vscode (if configured)
- [ ] Creating from a cookiecutter with no virtual environment doesn't open code
- [ ] "Virtualenv not requested, skipping" message should have a new line before it
- [ ] If user hits ctrl+c during pytoil init, the config is half written and can cause bugs later. Make it instead delete the whole thing unless run to completion
- [ ] "Project: project found on your GitHub" message in project checkout should be bold and blue like the others and have a new line before it
- [ ] "Unable to detect virtual environment, skipping" in project checkout should have new line before and after as comes after git clone output
- [ ] "project is available locally" should be in bold and blue not green to be consistent.
- [ ] 

## Longer Term Enhancements

- [ ] Add support for poetry? Need to add entry to config file
- [ ] Make it automatically install requirements if a file present
- [ ] Make it so you can pass packages to create that will be installed into the virtual environment after creation (or during creation for conda)
- [ ] Everything being under project feels clunkier than I thought it would. Would be good if we could instead do `pytoil checkout` `pytoil create` etc. rather than `pytoil project checkout`. If I remember right though, there are some issues doing this with Typer, everything to do with projects would have to live in `main.py` which might get messy.
