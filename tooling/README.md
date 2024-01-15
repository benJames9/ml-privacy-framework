## Multi arch images
https://docs.docker.com/build/building/multi-platform/
I used this command:
```
docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile.dev -t warmtea137/privacy-ml-segp:latest --push .
```