# Machine Learning Privacy Framework

## View the website publicly
If you have access to Imperial VPN, navigate to http://146.169.42.246 to view this web-application running.

## Run the application locally
You can run the application locally on your machine if you want to use your own GPU.

### Prerequisites
docker and docker-compose
CUDA configured with docker access

### Steps
Clone the repository
cd /tooling/
docker-compose up --build -d

Then after containers are built, navigate to http://localhost to view the application!

## Development
1. We'll be doing development using [VSCode](https://code.visualstudio.com/).
2. We'll be using Dev Containers in VSCode, so get [Docker](https://www.docker.com/) and the [dev containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers).
3. Then clone the repository locally, and do `Ctrl+Shift+P` or `Cmd+Shift+P`, select `>Dev Containers: Reopen in Container` and hit enter
4. This will use the `.devcontainer/devcontainer.json` to fetch the correct dev container, and setup the development environment with all the tools you'll need

Ensure to **write code while in the dev container**, since, especially for the Python stuff, you may come across specific issues which have been dealt with by the dev container setup.

### Tooling
- We'll use conventional commits via the [conventional-commit](https://pypi.org/project/conventional-commit/) pip package, i.e running `commitizen` to make it
- For branches, we'll eventually have `main` protected, and work primarily on the `develop` branch, branching off of that for `feature` branches and whatnot using [git flow](https://github.com/nvie/gitflow)
#### Git workflow
- Ensure git flow is initialised with `git flow init -d`
- Make sure to commit regularly using `cz commit` - it'll ask you some questions like what the scope of the commit is (what it has affected) etc
- Make sure to stay up to date with remote changes, `git fetch --all` and `git pull`


Here are the main `git flow` rules/commands we'll be adhering to:
- `git flow feature start [descriptive name of feature]` to start working on a specific feature - try not to make the features too long lived, but this is a loose restriction
  - Then merge it back in with `git flow feature finish` while on the feature branch
- `git flow release start [tag name]` the tag name should make it clear what is important about this release to make it a release
  - Then `git flow release finish` to finish working on this release while on the hotfix branch - it'll merge it back into `main` and `develop`
  - Also don't forget to do `git push origin --tags` to push the tagged release
- `git flow hotfix start [name of hotfix]` only use these when you come across a bug in `main` and immediately need to fix it
  - Finish it with `git flow hotfix finish` while on the hotfix branch
####
Use `./pull.sh` to pull files rather than `git pull`
