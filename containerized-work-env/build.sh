#!/bin/sh

# Make sure the required tools are installed
_check_required_tools() {
    ansible-playbook --version || return
}

_clean_leftover() {
    rm -f cid.stage-0 || return
    rm -f inventory || return
    rm -f work-env-image-id || return
}

_main() {
    local BASE_IMAGE
    local WORK_ENV_NAME
    local USER_NAME
    local GROUP_NAME
    local GIT_USER_EMAIL
    local GIT_USER_NAME
    local HOME_PATH_ON_HOST

    BASE_IMAGE="$1"
    WORK_ENV_NAME="$2"
    USER_NAME="$3"
    GROUP_NAME="$4"
    GIT_USER_EMAIL="$5"
    GIT_USER_NAME="$6"
    HOME_PATH_ON_HOST="$7"

    IMAGE_STAGE_0="containerized-work-env-${WORK_ENV_NAME}.stage-0"
    IMAGE_STAGE_1="containerized-work-env-${WORK_ENV_NAME}.stage-1"
    WORK_ENV_IMAGE="containerized-work-env-${WORK_ENV_NAME}"
    IMAGE_VERSION="ubuntu-22.04"  # TODO(ywen): Do not hard-code.

    docker image ls \
        --filter "label=name=${WORK_ENV_IMAGE}" \
        --filter "label=version=${IMAGE_VERSION}" \
        --format "{{.ID}}" > work-env-image-id || return

    WORK_ENV_IMAGE_ID=
    if [ -e work-env-image-id ]; then
        WORK_ENV_IMAGE_ID=$(cat work-env-image-id) || return
    fi

    if [ -z "$WORK_ENV_IMAGE_ID" ]; then
        echo "The Docker image '${WORK_ENV_IMAGE}:${IMAGE_VERSION}' does not exist. Creating it..." || return

        # The work env image does not exist yet so we need to create it.
        _check_required_tools || return

        _clean_leftover || return

        # Build image stage 0.
        docker build \
            --file Dockerfile.0 \
            --tag "${IMAGE_STAGE_0}:${IMAGE_VERSION}" \
            --label "name=${IMAGE_STAGE_0}" \
            --label "version=${IMAGE_VERSION}" \
            --build-arg BASE_IMAGE="${BASE_IMAGE}" \
            --build-arg WORK_ENV_NAME="${WORK_ENV_NAME}" \
            --build-arg USER_NAME="${USER_NAME}" \
            --build-arg GROUP_NAME="${GROUP_NAME}" \
            --build-arg GIT_USER_EMAIL="${GIT_USER_EMAIL}" \
            --build-arg GIT_USER_NAME="${GIT_USER_NAME}" \
            .  || return

        # Start stage 0 container for further configuration.
        docker run -d \
            --name "${IMAGE_STAGE_0}" \
            --cidfile cid.stage-0 \
            --tmpfs /tmp:exec \
            -v /etc/localtime:/etc/localtime:ro \
            --mount "type=bind,source=/home/${USER_NAME}/yaobin/.gnupg,destination=/tmp/.gnupg" \
            --mount "type=bind,source=/home/${USER_NAME}/yaobin/.gpg,destination=/tmp/.gpg" \
            "${IMAGE_STAGE_0}:${IMAGE_VERSION}" \
                /bin/sh -c 'while sleep 600; do :; done' || return

        # Run the Ansible provisioner.--file Dockerfile.0 \
        CID="$(cat "cid.stage-0")" || return
        echo "$CID ansible_user=root ansible_python_interpreter=auto" \
            >"inventory" || return

        ansible-playbook -vv -c docker -i "inventory" \
            -e "containerized_work_env_name='$WORK_ENV_NAME'" \
            -e "git_user_email='$GIT_USER_EMAIL'" \
            -e "git_user_full_name='$GIT_USER_NAME'" \
            -e "unprivileged_user_name='$USER_NAME'" \
            "containerized-work-env.yml" || return

        docker stop "$CID" || return

        docker commit "$CID" "${IMAGE_STAGE_1}:${IMAGE_VERSION}" || return

        # Start stage 1 container for further configuration.
        docker build \
            --file Dockerfile.2 \
            --tag "${WORK_ENV_IMAGE}:${IMAGE_VERSION}" \
            --label "name=${WORK_ENV_IMAGE}" \
            --label "version=${IMAGE_VERSION}" \
            --build-arg BASE_IMAGE="${IMAGE_STAGE_1}:${IMAGE_VERSION}" \
            --build-arg WORK_ENV_NAME="${WORK_ENV_NAME}" \
            --build-arg USER_NAME="${USER_NAME}" \
            --build-arg GROUP_NAME="${GROUP_NAME}" \
            .  || return

        docker image rm -f "${IMAGE_STAGE_0}:${IMAGE_VERSION}" || return
        docker image rm -f "${IMAGE_STAGE_1}:${IMAGE_VERSION}" || return
    else
        echo "The Docker image '${WORK_ENV_IMAGE}:${IMAGE_VERSION}' already exists." || return
    fi

    # Configure the host system.
    cd "${WORK_ENV_ROOT_DIR}/ansible" || return
    ansible-playbook -Kv \
      -e "containerized_work_env_name='$WORK_ENV_NAME'" \
      -e "containerized_work_env_image_name='$WORK_ENV_IMAGE'" \
      -e "containerized_work_env_image_version='$IMAGE_VERSION'" \
      -e "containerized_work_env_container_name='$WORK_ENV_IMAGE'" \
      -e "containerized_work_env_user_name='$USER_NAME'" \
      -e "home_path_on_host='$HOME_PATH_ON_HOST'" \
      containerized-work-env.yml || return
}

# Define the options and their corresponding variables
LONGOPTS="base-image:,work-env-name:,user-name:,group-name:,git-user-email:,git-user-name:,home-path-on-host:,help"

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
HOME_PATH_ON_HOST_DEFAULT="$HOME/yaobin"

# Set the initial values.
BASE_IMAGE="$BASE_IMAGE_DEFAULT"
WORK_ENV_NAME="$WORK_ENV_NAME_DEFAULT"
USER_NAME="$USER_NAME_DEFAULT"
GROUP_NAME="$GROUP_NAME_DEFAULT"
GIT_USER_EMAIL="$GIT_USER_EMAIL_DEFAULT"
GIT_USER_NAME="$GIT_USER_NAME_DEFAULT"
HOME_PATH_ON_HOST="$HOME_PATH_ON_HOST_DEFAULT"

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
        --home-path-on-host)
        echo "Option --home-path-on-host: $2"
        HOME_PATH_ON_HOST="$2"
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

_main "$BASE_IMAGE" "$WORK_ENV_NAME" "$USER_NAME" "$GROUP_NAME" "$GIT_USER_EMAIL" "$GIT_USER_NAME" "$HOME_PATH_ON_HOST"
