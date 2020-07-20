# Work Environment

## Overview

This repository has the scripts to set up my own work environment. See `Setup` section for the instructions.

## Setup

This setup guide assumes a freshly installed operating system with default settings. It's also written in the tone of "I" talking to "you": "I" am the present me and "you" are the future me.

### Bootstrap

First of all, get the content of this repository onto your computer. If you have `git` installed, you can use `git clone`; otherwise you can download the compressed package of this repository and unpack it somewhere. I'll assume it is unpacked at `$HOME/work-env`.

Decide the root folder of your own workspace. You can use any folder as you like, but I recommend `$HOME/yaobin` because it is the default location.

Run `bootstrap.sh` to install the required tools, such as `git`, `ansible`, `docker`, etc..

### Setup Work Environment

- 1). Run `ansible-playbook -Kvv -i ./ansible/inventory/localhost.yml ./ansible/my-ubuntu-desktop-14-04.yml`, or `my-ubuntu-desktop-18-04.yml`, depending on the version of Ubuntu.

### Setup YouTrack

- 1). Run `ansible-playbook -Kvv -i ./ansible/inventory/localhost.yml ./ansible/youtrack-server.yml`.
- 2). Open `http://localhost:8080` in a browser.
