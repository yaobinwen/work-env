# Virtual Machines

## Overview

Sometimes I need a virtual machine (VM) to experiment with things in order to avoid messing up with my host machine. This folder allows me to provision a VM of the specified operating system (OS) with the wanted environment.

I use `vagrant` to create the VMs and `ansible` to set up the environment inside the VMs.

## How to Use

- 1). Create a folder called `vm-<something>` [*] in which `something` is a reminder of its purpose.
- 2). Inside `vm-<something>`, use `vagrant` to initialize and create a VM.

Notes:

- [*] The `.gitignore` file ignores all the folders/files that start with `vm-`.
