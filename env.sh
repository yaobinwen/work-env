#!/bin/sh

test -e "./env.sh" || {
  echo "ERROR: 'env.sh' is not in the current path. Are you in the 'work-env' root folder?"
  return 1
}

export WORK_ENV_ROOT_DIR="$PWD"
export ANSIBLE_ROLES_PATH="$HOME/.ansible/roles:/usr/share/ansible/roles:/etc/ansible/roles:$WORK_ENV_ROOT_DIR/ansible/roles"
export ANSIBLE_FILTER_PLUGINS="$HOME/.ansible/plugins/filter:/usr/share/ansible/plugins/filter:$WORK_ENV_ROOT_DIR/ansible/filter_plugins"
export ANSIBLE_LIBRARY="$HOME/.ansible/plugins/modules:/usr/share/ansible/plugins/modules:$WORK_ENV_ROOT_DIR/ansible/library"
