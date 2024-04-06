#!/bin/sh

# Import `libs/config.sh`
. libs/config.sh

# As of 2024-03-05, we can use a different version but always use the `ubuntu`
# Docker image.
BASE_IMAGE_NAME="ubuntu"

# Make sure the required tools are installed
_check_required_tools() {
	ansible-playbook --version || return
}

_get_docker_image_id() {
	local IMAGE_NAME
	local IMAGE_VERSION
	local ID_FILE_NAME
	local IMAGE_ID

	IMAGE_NAME="$1"
	IMAGE_VERSION="$2"
	ID_FILE_NAME="$3"

	docker image ls \
		--filter "label=name=${IMAGE_NAME}" \
		--filter "label=version=${IMAGE_VERSION}" \
		--format "{{.ID}}" >"${ID_FILE_NAME}" || return

	IMAGE_ID=
	if [ -e "${ID_FILE_NAME}" ]; then
		IMAGE_ID=$(cat "${ID_FILE_NAME}") || return
	fi

	echo "${IMAGE_ID}"
}

_get_docker_container_id() {
	local CONTAINER_NAME
	local ID_FILE_NAME
	local CONTAINER_ID

	CONTAINER_NAME="$1"
	ID_FILE_NAME="$2"

	docker container ls \
		--filter "name=${CONTAINER_NAME}" \
		--format "{{.ID}}" >"${ID_FILE_NAME}" || return

	CONTAINER_ID=
	if [ -e "${ID_FILE_NAME}" ]; then
		CONTAINER_ID=$(cat "${ID_FILE_NAME}") || return
	fi
	rm -f "${ID_FILE_NAME}"

	echo "${CONTAINER_ID}"
}

_main() {
	local BASE_IMAGE_VERSION
	local WORK_ENV_NAME
	local USER_NAME
	local GROUP_NAME
	local GIT_USER_EMAIL
	local GIT_USER_NAME
	local HOME_PATH_ON_HOST

	BASE_IMAGE_VERSION="$1"
	WORK_ENV_NAME="$2"
	USER_NAME="$3"
	GROUP_NAME="$4"
	GIT_USER_EMAIL="$5"
	GIT_USER_NAME="$6"
	HOME_PATH_ON_HOST="$7"

	BASE_IMAGE="${BASE_IMAGE_NAME}:${BASE_IMAGE_VERSION}"
	IMAGE_VERSION="${BASE_IMAGE_NAME}-${BASE_IMAGE_VERSION}"
	STAGE_0_IMAGE_NAME="containerized-work-env-${WORK_ENV_NAME}.stage-0"
	IMAGE_STAGE_1="containerized-work-env-${WORK_ENV_NAME}.stage-1"
	WORK_ENV_IMAGE_NAME="containerized-work-env-${WORK_ENV_NAME}"

	WORK_ENV_IMAGE_ID=$(_get_docker_image_id "${WORK_ENV_IMAGE_NAME}" "${IMAGE_VERSION}" "iid.work-env")

	if [ -z "$WORK_ENV_IMAGE_ID" ]; then
		echo "The Docker image '${WORK_ENV_IMAGE_NAME}:${IMAGE_VERSION}' does not exist. Creating it..." || return

		# The work env image does not exist yet so we need to create it.
		_check_required_tools || return

		STAGE_0_IMAGE_ID=$(_get_docker_image_id "${STAGE_0_IMAGE_NAME}" "${IMAGE_VERSION}" "iid.stage-0")
		if [ -z "${STAGE_0_IMAGE_ID}" ]; then
			echo "The Docker image '${STAGE_0_IMAGE_NAME}:${IMAGE_VERSION}' does not exist. Creating it..." || return

			# Build image stage 0.
			docker build \
				--file Dockerfile.0 \
				--tag "${STAGE_0_IMAGE_NAME}:${IMAGE_VERSION}" \
				--label "name=${STAGE_0_IMAGE_NAME}" \
				--label "version=${IMAGE_VERSION}" \
				--build-arg BASE_IMAGE="${BASE_IMAGE}" \
				--build-arg WORK_ENV_NAME="${WORK_ENV_NAME}" \
				--build-arg USER_NAME="${USER_NAME}" \
				--build-arg GROUP_NAME="${GROUP_NAME}" \
				--build-arg GIT_USER_EMAIL="${GIT_USER_EMAIL}" \
				--build-arg GIT_USER_NAME="${GIT_USER_NAME}" \
				. || return
		else
			echo "The Docker image '${STAGE_0_IMAGE_NAME}:${IMAGE_VERSION}' already exists." || return
		fi

		STAGE_0_CONTAINER_ID=$(_get_docker_container_id "${STAGE_0_IMAGE_NAME}" "cid.stage-0")
		if [ -z "${STAGE_0_CONTAINER_ID}" ]; then
			echo "The Docker container '${STAGE_0_IMAGE_NAME}' does not exist. Starting it..." || return

			# Start stage 0 container for further configuration.
			docker run -d \
				--name "${STAGE_0_IMAGE_NAME}" \
				--cidfile cid.stage-0 \
				--tmpfs /tmp:exec \
				-v /etc/localtime:/etc/localtime:ro \
				--mount "type=bind,source=/home/${USER_NAME}/yaobin/.gnupg,destination=/tmp/.gnupg" \
				--mount "type=bind,source=/home/${USER_NAME}/yaobin/.gpg,destination=/tmp/.gpg" \
				"${STAGE_0_IMAGE_NAME}:${IMAGE_VERSION}" \
				/bin/sh -c 'while sleep 600; do :; done' || return
		else
			echo "The Docker container '${STAGE_0_IMAGE_NAME}' already exist." || return
		fi

		# Run the Ansible provisioner.--file Dockerfile.0 \
		CID="$(cat "cid.stage-0")" || return
		_config_containerized_work_env \
			"containerized-work-env.yml" \
			"$CID" \
			"$WORK_ENV_NAME" \
			"$GIT_USER_EMAIL" \
			"$GIT_USER_NAME" \
			"$USER_NAME" || return

		docker stop "$CID" || return

		docker commit "$CID" "${IMAGE_STAGE_1}:${IMAGE_VERSION}" || return

		# Start stage 1 container for further configuration.
		docker build \
			--file Dockerfile.2 \
			--tag "${WORK_ENV_IMAGE_NAME}:${IMAGE_VERSION}" \
			--label "name=${WORK_ENV_IMAGE_NAME}" \
			--label "version=${IMAGE_VERSION}" \
			--build-arg BASE_IMAGE="${IMAGE_STAGE_1}:${IMAGE_VERSION}" \
			--build-arg WORK_ENV_NAME="${WORK_ENV_NAME}" \
			--build-arg USER_NAME="${USER_NAME}" \
			--build-arg GROUP_NAME="${GROUP_NAME}" \
			. || return

		docker container rm -f "${STAGE_0_IMAGE_NAME}" || return
		docker image rm -f "${STAGE_0_IMAGE_NAME}:${IMAGE_VERSION}" || return
		docker image rm -f "${IMAGE_STAGE_1}:${IMAGE_VERSION}" || return
	else
		echo "The Docker image '${WORK_ENV_IMAGE_NAME}:${IMAGE_VERSION}' already exists." || return
	fi

	# Install the starter script.
	ansible-playbook -v \
		-e "containerized_work_env_name='$WORK_ENV_NAME'" \
		-e "containerized_work_env_image_name='$WORK_ENV_IMAGE_NAME'" \
		-e "containerized_work_env_image_version='$IMAGE_VERSION'" \
		-e "containerized_work_env_container_name='$WORK_ENV_IMAGE_NAME'" \
		-e "containerized_work_env_user_name='$USER_NAME'" \
		-e "home_path_on_host='$HOME_PATH_ON_HOST'" \
		host-work-env-starter-script.yml || return
}

# Define the options and their corresponding variables
LONGOPTS="base-image-version:,work-env-name:,user-name:,group-name:,git-user-email:,git-user-name:,home-path-on-host:,help"

# Parse the options
PARSED=$(getopt --options="$OPTIONS" --longoptions="$LONGOPTS" --name "$0" -- "$@")
echo "PARSED=$PARSED"

# Usage
USAGE="""Usage: $0 TODO(ywen): Add help info.
"""

# Evaluate the parsing results
eval set -- "$PARSED"

# Define the default values.
BASE_IMAGE_VERSION_DEFAULT="22.04"
WORK_ENV_NAME_DEFAULT="personal"
USER_NAME_DEFAULT="ywen"
GROUP_NAME_DEFAULT="ywen"
GIT_USER_EMAIL_DEFAULT="robin.wyb@gmail.com"
GIT_USER_NAME_DEFAULT="Yaobin Wen"
HOME_PATH_ON_HOST_DEFAULT="$HOME/yaobin"

# Set the initial values.
BASE_IMAGE_VERSION="$BASE_IMAGE_VERSION_DEFAULT"
WORK_ENV_NAME="$WORK_ENV_NAME_DEFAULT"
USER_NAME="$USER_NAME_DEFAULT"
GROUP_NAME="$GROUP_NAME_DEFAULT"
GIT_USER_EMAIL="$GIT_USER_EMAIL_DEFAULT"
GIT_USER_NAME="$GIT_USER_NAME_DEFAULT"
HOME_PATH_ON_HOST="$HOME_PATH_ON_HOST_DEFAULT"

# Process the options and arguments
while true; do
	case "$1" in
	--base-image-version)
		echo "Option --base-image-version: $2"
		BASE_IMAGE_VERSION="$2"
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

_main "$BASE_IMAGE_VERSION" "$WORK_ENV_NAME" "$USER_NAME" "$GROUP_NAME" "$GIT_USER_EMAIL" "$GIT_USER_NAME" "$HOME_PATH_ON_HOST"
