#!/bin/bash

# This sets up the basic system, and installs r5py and all other dependencies
# that are required to compute travel time matrices and prepare input and
# output data


# “strict mode”
set +m -euo pipefail
IFS=$'\n\t '


# 1. Update system packages
pacman --noconfirm -Syu


# 2. Install build-time dependencies (removed further down)
pacman --noconfirm \
    -S \
        --asdeps \
            base-devel \
            git \
            pacman-contrib \
            python-pip


# 3. Install some Python (etc.) packages system-wide (better runtime performance)
pacman --noconfirm \
    -S \
        jdk-openjdk \
        python-fiona \
        python-geopandas \
        python-joblib \
        python-pyproj \
        python-requests \
        python-shapely


# 4. Create a user to compile additional packages, allow it to run `sudo pacman`
useradd --create-home aurbuilder
echo "aurbuilder ALL=(ALL) NOPASSWD: ALL" >/etc/sudoers.d/10-aurbuilder


# 5. Install dependencies from the AUR
sudo -u aurbuilder /bin/bash <<EOF

    cd

    for PACKAGE in \
        include-what-you-use \
        protozero \
        libosmium
    do
        git clone "https://aur.archlinux.org/\${PACKAGE}.git"
        cd "\${PACKAGE}"
        makepkg --noconfirm --syncdeps --rmdeps --install --asdeps
        cd ..
    done

    for PACKAGE in \
        python-jpype1 \
        osmium-tool
    do
        git clone "https://aur.archlinux.org/\${PACKAGE}.git"
        cd "\${PACKAGE}"
        makepkg --noconfirm --syncdeps --rmdeps --install
        cd ..
    done
EOF


# 6. Remove the build user
userdel --remove aurbuilder
rm -v /etc/sudoers.d/10-aurbuilder


# 7. Create an unprivileged user
useradd --create-home dgl


# 8. Install r5py into this unprivileged user’s ~/.local/
#    and run its unit-tests
sudo -u dgl /bin/bash <<EOF
    cd
    pip install --upgrade "r5py[tests] @ git+https://github.com/r5py/r5py.git"

    # clone source tree (with tests + test data)
    git clone https://github.com/r5py/r5py.git

    # run tests
    cd r5py
    python -m pytest

    # delete source tree
    cd
    rm -R r5py
EOF


# 9. Clean pacman cache, and uninstall unneeded packages
paccache -rk0
while (pacman -Qttdq | pacman --noconfirm -Rsndc -)
    do
        sleep 0.1
    done


# 10. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
