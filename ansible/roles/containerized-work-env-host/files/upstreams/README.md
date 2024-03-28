# Folder "upstreams"

## Overview

This folder contains the upstreams of the mirror repositories.

The mirrored repository is checked out in the folder "code".

## Duplicating a repository

See [_GitHub: Duplicating a repository_](https://docs.github.com/en/repositories/creating-and-managing-repositories/duplicating-a-repository).

- On GitHub, create a repository to be the mirror of the upstream repository: `https://github.com/yaobinwen/mirror-repo`
- `git clone --mirror https://<git-host>/<upstream-reop>.git`.
- `cd <upstream-repo>.git`.
- `git remote set-url --push origin git@github.com:yaobinwen/<mirror-repo>.git`.
  - As with a bare clone, a mirrored clone includes all remote branches and tags, but all local references will be overwritten each time you fetch, so it will always be the same as the original repository. Setting the URL for pushes simplifies pushing to your mirror.
- To update your mirror, fetch updates and push:
  - `git fetch -p origin`
  - `git push --mirror`
