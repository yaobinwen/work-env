#!/bin/sh

# Echo the commands.
set -x

# Detect the environment.
OS_NAME=$(lsb_release --id --short)
OS_VERSION=$(lsb_release --release --short)
OS_CODENAME=$(lsb_release --codename --short)
ARCHITECTURE=$(uname --processor)

# Debugging output.
cat <<__EOS__ || exit
OS_NAME=${OS_NAME}
OS_VERSION=${OS_VERSION}
OS_CODENAME=${OS_CODENAME}
ARCHITECTURE=${ARCHITECTURE}
__EOS__

# Check we are running on a supported platform.
test "${OS_NAME}" = "Ubuntu" -a $(dpkg --compare-versions "${OS_VERSION}" ge "14.04"; echo $?) = "0" || {
    echo "Error: We only support Ubuntu 14.04 and later, but the current OS is ${OS_NAME} ${OS_VERSION}.";
    exit 2;
}

test ${ARCHITECTURE} = "x86_64" || {
    echo "Error: We only support 'x86_64' platform.";
    exit 2;
}

# Decide the APT tool.
APT_GET="apt-get"
if [ $(dpkg --compare-versions "${OS_VERSION}" ge "18.04"; echo $?) = "0" ]; then
    APT_GET="apt"
fi

# Update the APT package list.
sudo ${APT_GET} update

# Install software-properties-common so we can use apt-add-repository.
sudo ${APT_GET} --yes install software-properties-common

# Add PPAs
# Git: https://launchpad.net/~git-core/+archive/ubuntu/ppa
if [ "{OS_VERSION}" = "14.04" ]; then
    sudo apt-add-repository --yes ppa:git-core/ppa
fi
# Ansible: https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html#latest-releases-via-apt-ubuntu
sudo apt-add-repository --yes ppa:ansible/ansible

# Update the APT package list after adding all the PPAs.
sudo ${APT_GET} update

# Install the required tools.
sudo ${APT_GET} --yes install \
    git \
    ansible
