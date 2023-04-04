#!/bin/bash

# This sets up the basic system, and installs r5py and all other dependencies
# that are required to compute travel time matrices and prepare input and
# output data


# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '


# 8. Install r5py into this unprivileged user’s ~/.local/
#    and run its unit-tests
sudo -u dgl /bin/bash <<EOF
    cd
    pip install git+https://github.com/r5py/r5py.git

    pip install pytest pytest-asyncio pytest-cov pytest-lazy-fixture

    # clone source tree (with tests + test data)
    git clone https://github.com/r5py/r5py.git

    # run tests
    cd r5py
    python -m pytest

    # delete source tree and uninstall test dependencies
    cd
    rm -R r5py
    pip uninstall -y pytest pytest-asyncio pytest-cov pytest-lazy-fixture
EOF


# 99. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
