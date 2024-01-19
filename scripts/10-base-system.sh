#!/bin/bash

# This sets up the basic system, and installs r5py and all other dependencies
# that are required to compute travel time matrices and prepare input and
# output data


# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '


# 1. Update system packages
apt-get update
apt-get --yes upgrade


# 2. Install system-wide dependencies
apt-get --yes install \
    build-essential \
    openjdk-21-jre \
    git \
    osmium-tool \
    p7zip-full \
    python3 \
    python3-gdal \
    python3-pip \
    sudo


# 3. upgrade pip (breaking things, but fine)
pip install --upgrade pip


# 7. Create an unprivileged user
useradd --create-home dgl


# 99. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
