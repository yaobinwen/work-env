#!/bin/sh

set -x

vagrant up || exit

vagrant provision --provision-with "sandbox-play" || exit

vagrant halt || exit
