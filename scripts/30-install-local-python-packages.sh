#!/bin/bash

# This sets up the basic system, and installs r5py and all other dependencies
# that are required to compute travel time matrices and prepare input and
# output data


# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '


# 9. Install local python packages
chown -R dgl:dgl /tmp/python-packages/
sudo -u dgl /bin/bash <<EOF
    ls -1d /tmp/python-packages/* | while read PACKAGE
        do
            pip install "\${PACKAGE}"
        done
EOF


# 99. Clean-up: remove ourselves
rm -Rv /tmp/python-packages/
rm -v -- "${BASH_SOURCE[0]}"
