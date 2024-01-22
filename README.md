# Machine Learning Privacy Framework

## Development
1. We'll be doing development using [VSCode](https://code.visualstudio.com/).
2. We'll be using Dev Containers in VSCode, so get [Docker](https://www.docker.com/) and the [dev containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
3. Then clone the repository locally, and do `Ctrl+Shift+P` or `Cmd+Shift+P`, select `>Dev Containers: Reopen in Container` and hit enter
4. This will use the `.devcontainer/devcontainer.json` to fetch the correct dev container, and setup the development environment with all the tools you'll need

### Tooling
#### Git Conventions
- We'll use conventional commits via the [conventional-commit](https://pypi.org/project/conventional-commit/) pip package, i.e running `commitizen` to make it
- For branches, we'll eventually have `main` protected, and work primarily on the `develop` branch, branching off of that for `feature` branches and whatnot using [git flow](https://github.com/nvie/gitflow)
