## Dev Container Features
- Various useful common commandline utilities such as `vim`, `htop`, `tree` and `fzf`, as well as the default shell being `zsh` with an autocompletion plugin installed
- Various Python and Git additions to make them more useful (more in the main README.md)
- JS stuff for the frontend

## Multi arch images
https://docs.docker.com/build/building/multi-platform/
I used this command:
```
docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.dev -t warmtea137/privacy-ml-segp:latest --push .
```