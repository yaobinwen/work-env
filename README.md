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

### Step 3: Set up Work Environment

- 1). Determine the work environment you want to set up, including:
  - The target machine (e.g., `localhost`).
  - The host operating system (e.g., Ubuntu 18.04).
  - The code committer variables, including at least (see the `code-committer-<name>.yml` for all the variables):
    - `code_committer_ssh_private_key_file_path`
    - `code_committer_host_code_root_dir`
- 2). Run `cd ./ansible`.
- 3). Run `ansible-galaxy collection install -r ./ansible-requirements.yml` to install the needed Ansible collections.
- 4). Run `ansible-galaxy role install -r ./ansible-requirements.yml` to install the needed Ansible roles.
- 3). Run `ansible-playbook -Kvvv ./my-ubuntu-desktop-18.04.yml`.
- 4). Run `ansible-playbook -vvv -e code_committer_ssh_private_key_file_path="/path/to/SSH-private-key" -e code_committer_gpg_signing_subkey_file_path="/path/to/GPG-signing-subkey" -e code_committer_host_code_root_dir="/path/to/code/root-dir" code-committer-personal.yml`.

### Step 4: Set up Printer

As of 2023-03-31, I am using a `Brother MFC-7860DW` printer/scanner. Follow the steps below to set up the driver:

- 1). Connect the printer to the local network and power it on.
- 2). Figure out the IP address of the printer:
  - a). Run `avahi-browse -kart` to browse all the available devices. Look for the section for `Brother MFC-7860DW`.
  - b). My printer's hostname is `BRN30055C086C0F.local`. So I can just run `ping BRN30055C086C0F.local` to get the IP address.
- 3). Go to the [Downloads page](https://support.brother.com/g/b/downloadtop.aspx?c=us&lang=en&prod=mfc7860dw_all).
- 4). Select `Linux` -> `Linux (deb)`. Click `OK`.
- 5). Click `Driver Install Tool` which says "The tool will install LPR, CUPSwrapper driver and scanner driver (for scanner models)."
- 6). Click "Agree to the EULA and Download" to trigger the download.
- 7). Follow the "How to Install" steps to finish the actual installation. Some notes:
  - a). To run the installation script, I should provide `MFC-7860DW` as the input argument.
  - b). Because I am using a network printer, I should enter `yes` to the question "Will you specify the DeviceURI ?", and then enter the IP address of the printer.
