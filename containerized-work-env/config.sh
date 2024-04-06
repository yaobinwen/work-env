#!/bin/sh

# Import `libs/config.sh`
. libs/config.sh

# Figure out the default values.
DEFAULT_ANSIBLE_PLAYBOOK="containerized-work-env.yml"
DEFAULT_CID_FILE="/tmp/cid.containerized-work-env-personal"
DEFAULT_WORK_ENV_NAME="personal"
DEFAULT_GIT_USER_EMAIL="robin.wyb@gmail.com"
DEFAULT_GIT_USER_NAME="Yaobin Wen"
DEFAULT_USER_NAME="ywen"

# Define the options and their corresponding variables
LONGOPTS="ansible-playbook:,cid-file:,work-env-name:,git-user-email:,git-user-name:,user-name:,help"

# Parse the options
PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
echo "PARSED=$PARSED"

# Usage
USAGE="""Usage: $0 [OPTIONS]

  --ansible-playbook:   Use the specified Ansible playbook to configure the work env (default: $DEFAULT_ANSIBLE_PLAYBOOK).
  --cid-file:           The CID file of the containerized work env Docker container (default: $DEFAULT_CID_FILE).
  --work-env-name:      Work env's name (default: $DEFAULT_WORK_ENV_NAME).
  --git-user-email:     Use this email to configure git (default: $DEFAULT_GIT_USER_EMAIL).
  --git-user-name:      Use this name to configure git (default: $DEFAULT_GIT_USER_NAME).
  --user-name:          The primary user name in the containerized work env.
  --help:               Show this help message.
"""

# Evaluate the parsing results
eval set -- "$PARSED"

# Set the initial values.
ANSIBLE_PLAYBOOK="$DEFAULT_ANSIBLE_PLAYBOOK"
CID_FILE="$DEFAULT_CID_FILE"
WORK_ENV_NAME="$DEFAULT_WORK_ENV_NAME"
GIT_USER_EMAIL="$DEFAULT_GIT_USER_EMAIL"
GIT_USER_NAME="$DEFAULT_GIT_USER_NAME"
USER_NAME="$DEFAULT_USER_NAME"

# Process the options and arguments
while true; do
	case "$1" in
	--ansible-playbook)
		echo "Option --ansible-playbook: $2"
		ANSIBLE_PLAYBOOK="$2"
		shift 2
		;;
	--cid-file)
		echo "Option --cid-file: $2"
		CID_FILE="$2"
		shift 2
		;;
	--work-env-name)
		echo "Option --work-env-name: $2"
		WORK_ENV_NAME="$2"
		shift 2
		;;
	--git-user-email)
		echo "Option --git-user-email: $2"
		GIT_USER_EMAIL="$2"
		shift 2
		;;
	--git-user-name)
		echo "Option --git-user-name: $2"
		GIT_USER_NAME="$2"
		shift 2
		;;
	--user-name)
		echo "Option --user-name: $2"
		USER_NAME="$2"
		shift 2
		;;
	--help)
		echo "$USAGE"
		exit 0
		;;
	--)
		shift
		break
		;;
	*)
		echo "Unknown option: $1"
		exit 1
		;;
	esac
done

CID="$(cat "/tmp/cid.containerized-work-env-personal")" || return

_config_containerized_work_env \
	"$ANSIBLE_PLAYBOOK" \
	"$CID" \
	"$WORK_ENV_NAME" \
	"$GIT_USER_EMAIL" \
	"$GIT_USER_NAME" \
	"$USER_NAME"
