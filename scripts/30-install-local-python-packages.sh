#!/bin/bash

# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '


# 1. Install local python packages
sudo -u dgl /bin/bash <<EOF
    pip \
        install \
            --user \
            --break-system-packages \
            git+https://github.com/DigitalGeographyLab/travel-time-matrix-computer.git
EOF


# 99. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
