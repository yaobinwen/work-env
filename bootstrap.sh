#!/bin/sh

# Echo the commands.
set -x

# Constants.
EXPECTED_ARCHITECTURE="x86_64"
EXPECTED_OS="Ubuntu"
MINIMUM_OS_VERSION="18.04"

# Detect the environment.
OS_NAME=$(lsb_release --id --short)
OS_VERSION=$(lsb_release --release --short)
OS_CODENAME=$(lsb_release --codename --short)
ARCHITECTURE=$(uname --processor)

# Debugging output.
cat <<__EOS__ || exit
EXPECTED_ARCHITECTURE=${EXPECTED_ARCHITECTURE}
EXPECTED_OS=${EXPECTED_OS}
MINIMUM_OS_VERSION=${MINIMUM_OS_VERSION}
OS_NAME=${OS_NAME}
OS_VERSION=${OS_VERSION}
OS_CODENAME=${OS_CODENAME}
ARCHITECTURE=${ARCHITECTURE}
__EOS__

# Check we are running on a supported platform.
test "${OS_NAME}" = "${EXPECTED_OS}" || {
    echo "Error: We only support the OS '${EXPECTED_OS}', but the current OS is '${OS_NAME}'."
    exit 2
}

if dpkg --compare-versions "${OS_VERSION}" lt "${MINIMUM_OS_VERSION}"; then
    echo "Error: We only support ${EXPECTED_OS} ${MINIMUM_OS_VERSION} and later, but the current OS is ${OS_NAME} ${OS_VERSION}."
    exit 2
fi

test ${ARCHITECTURE} = "${EXPECTED_ARCHITECTURE}" || {
    echo "Error: We only support '${EXPECTED_ARCHITECTURE}' platform."
    exit 2
}

# Update the APT package list.
sudo apt-get update || exit

# Install software-properties-common so we can use apt-add-repository.
sudo apt-get --yes install software-properties-common || exit

# Add Ansible PPA
# https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#latest-releases-via-apt-ubuntu
sudo apt-add-repository --yes --no-update ppa:ansible/ansible || exit

# Update the APT cache after adding all the PPAs.
sudo apt-get update || exit

# Install the required tools.
sudo apt-get --yes install \
    ansible \
    python3 \
        || exit

# Set up a temporary storage.
TMP_DIR=$(mktemp --directory) || exit

cleanup() {
    rm -fr "$TMP_DIR" || echo "WARNING: cleanup() failed" >&2
}
trap cleanup EXIT INT TERM

# Find all the Ansible requirements files.
find . -name "ansible-requirements.yml" -type f -print0 > "$TMP_DIR/ANSIBLE_REQUIREMENTS_FILES" || exit

# Install the needed Ansible roles/collections.
xargs --arg-file "$TMP_DIR/ANSIBLE_REQUIREMENTS_FILES" -0 --no-run-if-empty --verbose -I"{}" \
    ansible-galaxy install -r "{}" || exit
