# Work Environment

## Overview

This repository has the scripts to set up my own work environment. See `Setup` section for the instructions.

## Setup

This setup guide assumes a freshly installed operating system with default settings. It's also written in the tone of "I" talking to "you": "I" am the present me and "you" are the future me.

### Bootstrap

First of all, get the content of this repository onto your computer. If you have `git` installed, you can use `git clone`; otherwise you can download the compressed package of this repository and unpack it somewhere. I'll assume it is unpacked at `$HOME/work-env`.

Decide the root folder of your own workspace. You can use any folder as you like, but I recommend `$HOME/yaobin` because it is the default location.

Run `bootstrap.sh` to install the required tools, such as `git`, `ansible`, `docker`, etc..

### Setup YouTrack

- 1). Run `ansible-playbook -Kvv -i ./ansible/inventory/localhost.yml ./ansible/youtrack-server.yml`.
- 2). Open `http://localhost:8080` in a browser.

### Setup GitHub Container

- 1). Change into `docker` folder.
- 2). Copy the SSH private key of your personal GitHub account into the `docker/github` folder and name it `id_rsa.personal`.
- 3). Run `docker-compose -f docker-compose-build.yml build` to build the docker images:
  - `github-container`
- 4). Run `GITHUB_ROOT_DIR="$HOME/yaobin/github" docker-compose up -d` to start the GitHub container.
- 5). Delete the `id_rsa.personal` from the `docker/github` folder.
