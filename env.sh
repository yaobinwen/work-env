#!/bin/sh

export ANSIBLE_ROLES_PATH="$HOME/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles:$PWD/ansible/roles"
export ANSIBLE_FILTER_PLUGINS="$HOME/.ansible/plugins/filter:/usr/share/ansible/plugins/filter:$PWD/ansible/filter_plugins"
export ANSIBLE_LIBRARY="$HOME/.ansible/plugins/modules:/usr/share/ansible/plugins/modules:$PWD/ansible/library"
