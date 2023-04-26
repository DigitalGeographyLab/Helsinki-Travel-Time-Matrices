#!/bin/bash

# This sets up the basic system, and installs r5py and all other dependencies
# that are required to compute travel time matrices and prepare input and
# output data


# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '


# 10. Clean pacman cache, and uninstall unneeded packages
paccache -rk0
while (pacman -Qtdq | pacman --noconfirm -Rsndc -)
    do
        sleep 0.1
    done


# 11. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
