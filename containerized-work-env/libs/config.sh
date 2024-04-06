#!/bin/sh

_config_containerized_work_env() {
	test $# -eq 6 || {
		echo "_config_containerized_work_env <ANSIBLE_PLAYBOOK> <CID> <WORK_ENV_NAME> <GIT_USER_EMAIL> <GIT_USER_NAME> <USER_NAME>"
		return 1
	}

	local ANSIBLE_PLAYBOOK CID WORK_ENV_NAME GIT_USER_EMAIL GIT_USER_NAME USER_NAME

	ANSIBLE_PLAYBOOK="$1"
	CID="$2"
	WORK_ENV_NAME="$3"
	GIT_USER_EMAIL="$4"
	GIT_USER_NAME="$5"
	USER_NAME="$6"

	echo "$CID ansible_user=root ansible_python_interpreter=auto" \
		>"inventory" || return

	ansible-playbook -vv -c docker -i "inventory" \
		-e "containerized_work_env_name='$WORK_ENV_NAME'" \
		-e "git_user_email='$GIT_USER_EMAIL'" \
		-e "git_user_full_name='$GIT_USER_NAME'" \
		-e "work_env_user_name='$USER_NAME'" \
		"$ANSIBLE_PLAYBOOK" || return
}
