ARG UBUNTU_VERSION=14.04
FROM ubuntu:${UBUNTU_VERSION}
ARG USER_NAME=ywen
ARG USER_ID=1000
ARG GROUP_ID=1000

RUN groupadd -g ${GROUP_ID} ${USER_NAME} && \
    useradd -r --create-home -u ${USER_ID} -g ${USER_NAME} ${USER_NAME}

# Install software-properties-common so we can use add-apt-repository.
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install \
    software-properties-common

# Install git.
RUN add-apt-repository -y ppa:git-core/ppa && \
    apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install git

# Install other necessary packages.
RUN DEBIAN_FRONTEND=noninteractive apt-get -y --force-yes install \
    openssh-server \
    openssh-client \
    vim

# Switch to the non-root user.
USER ${USER_NAME}

# Configure git.
RUN git config --global user.email "robin.wyb@gmail.com"
RUN git config --global user.name "Yaobin Wen"

# Copy the SSH private key.
COPY ./id_rsa.personal /tmp/id_rsa
RUN mkdir -pv ${HOME}/.ssh
RUN cp /tmp/id_rsa ${HOME}/.ssh/id_rsa
RUN chmod 600 ${HOME}/.ssh/id_rsa