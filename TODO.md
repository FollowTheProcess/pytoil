# TODO

Below are a list of enhancements or fixes discovered during pre-release testing:

## Immediate Fixes

### Easy Tweaks

- [x] Ensure all examples in help say "Examples" not "Example"
- [x] Add clarifying message to pytoil init when config file already exists saying it's checking or something
- [x] "Removing project: project" should be yellow maybe?
- [x] "Project: project found on your GitHub" message in project checkout should be bold and blue like the others and have a new line before it
- [x] "Unable to detect virtual environment, skipping" in project checkout should have new line before and after as comes after git clone output
- [x] "project is available locally" should be in bold and blue not green to be consistent.
- [x] "Virtualenv not requested, skipping" message should have a new line before it
- [x] README still shows old cookiecutter option, change to --cookie
- [x] pytoil init initial message "checking config" should be bold and blue to be consistent with others
- [x] pytoil init "something's wrong in the config file" needs a new line after it

### Legit Changes Requiring Tests

- [x] Setting python path in vscode settings errors if file is missing or it's empty
- [x] Creating from a cookiecutter with no virtual environment doesn't open code
- [x] Pytoil config show raises ugly FileNotFound error when config file doesn't exist
- [x] Same with config set
- [x] Make pytoil init check more robust than just whether or not the file exists. See if it has the right keys etc. Or even just a check that it's not empty.
- [x] Creating a new conda project when the environment already exists raises an ugly error. Should instead just set the python path in vscode (if configured)
- [ ] If user hits ctrl+c during pytoil init, the config is half written and can cause bugs later. Make it instead delete the whole thing unless run to completion. Maybe a try except on `KeyboardInterrupt`? Or is this dangerous? Might never terminate etc.

## Longer Term Enhancements

- [ ] Add support for poetry? Need to add entry to config file
- [ ] Make it automatically install requirements if a file present
- [ ] Make it so you can pass packages to create that will be installed into the virtual environment after creation (or during creation for conda)
- [ ] Everything being under project feels clunkier than I thought it would. Would be good if we could instead do `pytoil checkout` `pytoil create` etc. rather than `pytoil project checkout`. If I remember right though, there are some issues doing this with Typer, everything to do with projects would have to live in `main.py` which might get messy.
- [ ] Add a config check command that more closely inspects the config file and does some validation
- [ ] Option to make a git repo on create, maybe a GitHub repo too and link them? Or is this better left to the gh cli?
