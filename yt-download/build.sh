#!/bin/sh

set -x

docker build \
    --file Dockerfile.yt-download \
    --tag yt-download:ubuntu-22.04 \
    .

docker run \
    --detach \
    --name yt-download \
    --rm \
    --interactive \
    --tty \
    --volume "$PWD:/yt-download:rw" \
    --volume "$HOME/Downloads:/Downloads:rw" \
    --workdir "/Downloads" \
    yt-download:ubuntu-22.04 \
    /bin/bash
