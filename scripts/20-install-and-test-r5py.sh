#!/bin/bash

# This sets up the basic system, and installs r5py and all other dependencies
# that are required to compute travel time matrices and prepare input and
# output data


# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '

R5PY_GIT_URL="https://github.com/r5py/r5py.git@342803f"
RUN_TESTS=false

# 8. Install r5py into this unprivileged user’s ~/.local/
sudo -u dgl /bin/bash <<EOF
    cd

    pip install --user --break-system-packages "git+${R5PY_GIT_URL}"

    if [[ "${RUN_TESTS}" = true ]]; then
        git clone "${R5PY_GIT_URL}"
        cd r5py

        python -m venv .virtualenv
        source .virtualenv/bin/activate
        pip install .[tests]

        python -m pytest

        cd ..
        rm -Rf r5py
    fi
EOF


# 99. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
