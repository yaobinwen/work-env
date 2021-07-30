# Work Environment

## Overview

This repository has the scripts to set up my own work environment. See `Setup` section for the instructions.

## Setup

### Step 0: Prerequisites

1. A freshly installed Ubuntu 18.04 or later.
2. Cell phone with the app `Authenticator` available for GitHub's two-factor authentication.

### Step 1: Download This Repo

Because this is a freshly installed OS, `git`, as well as the personal SSH private key, is unlikely to be set up yet. Therefore, you will need to use the `Download ZIP` function on GitHub to download this repository.

Decompress the `.zip` file after downloading.

### Step 2: Bootstrap

Change into the root of the decompressed folder so you will find the script `bootstrap.sh`.

Run `sudo ./bootstrap.sh` to install the initial tools (mainly `ansible`) for further setup.

### Step 3: Setup Work Environment

- 1). Determine the work environment you want to set up, including:
  - The target machine (e.g., `localhost`).
  - The host operating system (e.g., Ubuntu 18.04).
  - The code committer variables, including at least (see the `code-committer-<name>.yml` for all the variables):
    - `code_committer_ssh_private_key_file_path`
    - `code_committer_host_code_root_dir`
- 2). Run `cd ./ansible`.
- 3). Run `ansible-playbook -Kvvv ./my-ubuntu-desktop-18.04.yml`.
- 4). Run `ansible-playbook -vvv -e code_committer_ssh_private_key_file_path="/path/to/SSH-private-key" -e code_committer_host_code_root_dir="/path/to/code/root-dir" code-committer-personal.yml`.

### Step N: Additional Setup

Set up `YouTrack`:

- 1). Run `ansible-playbook -Kvv ./youtrack-server.yml`.
- 2). Open `http://localhost:8080` in a browser.
