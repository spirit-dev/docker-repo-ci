# DockerFiles

This repository is dedicated to oficial images used in our differents projects / microservices

**Technically speaking**

- CICD in place to ease build and push of images
- Testing solution for images
- Easier tagging strategy
- Harmonization of naming convention

**Organization view**
​

- Easier security patches for the entire organization
- storage possibility for non-service related images
- Collaborative improvment on images
- More control on language version
- Easier deprecation system
- Less confusion (what image should I use ?)
- Better resillience, reliability and trust

## Documentation

### Os

- [**Alpine**](images/os/alpine/Readme.md)

## Test

### Prerequisite

Install the unit test tool

**FOR macOS**:
GNU 3.81 is installed by default. To execute `.ONESHELL` commands, 3.82 and higher is required.

```shell
brew install make
```

Then add `PATH="/usr/local/opt/make/libexec/gnubin:$PATH"` to your `.bashrc` or `.zshrc`. Then source or reload your terminal screen.

Validation:

```shell
make --version

GNU Make 4.3
Built for x86_64-apple-darwin19.6.0
Copyright (C) 1988-2020 Free Software Foundation, Inc.
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
```

### Linux

```shell
curl -LO https://storage.googleapis.com/container-structure-test/latest/container-structure-test-linux-amd64 && chmod +x container-structure-test-linux-amd64 && sudo mv container-structure-test-linux-amd64 /usr/local/bin/container-structure-test
```

### MacOS

```shell
curl -LO https://storage.googleapis.com/container-structure-test/latest/container-structure-test-darwin-amd64 && chmod +x container-structure-test-darwin-amd64 && sudo mv container-structure-test-darwin-amd64 /usr/local/bin/container-structure-test
```

### Others

```shell
docker pull zemanlx/container-structure-test:v1.8.0-alpine
```

```shell
alias container-structure-test="docker run -i --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/code/dockerfiles:/test \
  zemanlx/container-structure-test:v1.8.0-alpine "
```

### Usage

```shell
container-structure-test test --image tbd/{IMAGES}:{TAG} --config {TEST_FILE}.yaml

```

## Resource

- <https://linux.die.net/man/1/make>
- <https://github.com/GoogleContainerTools/container-structure-test>
- <https://docs.docker.com/engine/reference/builder/>
