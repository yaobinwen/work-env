#!/bin/sh

# Make sure the required tools are installed
_check_required_tools() {
  ansible-playbook --version || return
}

_clean_leftover() {
  rm -f cid.stage-0 || return
  rm -f inventory || return
}

_main() {
  local BASE_IMAGE
  local WORK_ENV_NAME
  local USER_NAME
  local GROUP_NAME
  local GIT_USER_EMAIL
  local GIT_USER_NAME

  BASE_IMAGE="$1"
  WORK_ENV_NAME="$2"
  USER_NAME="$3"
  GROUP_NAME="$4"
  GIT_USER_EMAIL="$5"
  GIT_USER_NAME="$6"

  IMAGE_STAGE_0="containerized-work-env-${WORK_ENV_NAME}.stage-0"
  WORK_ENV_IMAGE="containerized-work-env-${WORK_ENV_NAME}"

  _check_required_tools || return

  _clean_leftover || return

  # Build image stage 0.
  docker build \
      -f Dockerfile.0 \
      -t "${IMAGE_STAGE_0}" \
      --build-arg BASE_IMAGE="${BASE_IMAGE}" \
      --build-arg WORK_ENV_NAME="${WORK_ENV_NAME}" \
      --build-arg USER_NAME="${USER_NAME}" \
      --build-arg GROUP_NAME="${GROUP_NAME}" \
      --build-arg GIT_USER_EMAIL="${GIT_USER_EMAIL}" \
      --build-arg GIT_USER_NAME="${GIT_USER_NAME}" \
        .   || return

  # Start stage 0 container for further configuration.
  docker run -d \
      --cidfile cid.stage-0 \
      --tmpfs /tmp:exec \
      -v "$PWD:/build:ro" \
      -v /etc/localtime:/etc/localtime:ro \
      "${IMAGE_STAGE_0}" \
          /bin/sh -c 'while sleep 3600; do :; done' || return

    # Run the Ansible provisioner.
    CID="$(cat "cid.stage-0")" || return
    echo "$CID ansible_user=${USER_NAME} ansible_python_interpreter=auto" \
        >"inventory" || return

    ansible-playbook -vv -c docker -i "inventory" \
      -e "git_user_email='$GIT_USER_EMAIL'" \
      -e "git_user_full_name='$GIT_USER_NAME'" \
      -e "locale_user_name='$USER_NAME'" \
      "containerized-work-env.yml" || return

    docker stop "$CID" || return

    docker commit "$CID" "$WORK_ENV_IMAGE" || return
}

# Define the options and their corresponding variables
LONGOPTS="base-image:,work-env-name:,user-name:,group-name:,git-user-email:,git-user-name:,help"

# Parse the options
PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
echo "PARSED=$PARSED"

# Usage
USAGE="""Usage: $0 TODO(ywen): Add help info.
"""

# Evaluate the parsing results
eval set -- "$PARSED"

# Define the default values.
BASE_IMAGE_DEFAULT="ubuntu:22.04"
WORK_ENV_NAME_DEFAULT="personal"
USER_NAME_DEFAULT="ywen"
GROUP_NAME_DEFAULT="ywen"
GIT_USER_EMAIL_DEFAULT="robin.wyb@gmail.com"
GIT_USER_NAME_DEFAULT="Yaobin Wen"

# Set the initial values.
BASE_IMAGE="$BASE_IMAGE_DEFAULT"
WORK_ENV_NAME="$WORK_ENV_NAME_DEFAULT"
USER_NAME="$USER_NAME_DEFAULT"
GROUP_NAME="$GROUP_NAME_DEFAULT"
GIT_USER_EMAIL="$GIT_USER_EMAIL_DEFAULT"
GIT_USER_NAME="$GIT_USER_NAME_DEFAULT"

# Process the options and arguments
while true; do
  case "$1" in
    --base-image)
      echo "Option --base-image: $2"
      BASE_IMAGE="$2"
      shift 2
      ;;
    --work-env-name)
      echo "Option --work-env-name: $2"
      WORK_ENV_NAME="$2"
      shift 2
      ;;
    --user-name)
      echo "Option --user-name: $2"
      USER_NAME="$2"
      shift 2
      ;;
    --group-name)
      echo "Option --group-name: $2"
      GROUP_NAME="$2"
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

_main "$BASE_IMAGE" "$WORK_ENV_NAME" "$USER_NAME" "$GROUP_NAME" "$GIT_USER_EMAIL" "$GIT_USER_NAME"
