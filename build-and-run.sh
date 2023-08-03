#!/bin/bash

set +m -euo pipefail
IFS=$'\n\t '

DATA_DIRECTORY="$(realpath $(dirname ${0}))/data"

docker build --network=host --tag helsinki-ttm --ulimit nofile=1024:524288 .

docker run \
    --network=host \
    -it \
    -u $(id -u):$(id -g) \
    -e LD_PRELOAD="/usr/lib/jvm/default/lib/libjsig.so" \
    -v "${DATA_DIRECTORY}:/data" \
    helsinki-ttm \
    "$@"
