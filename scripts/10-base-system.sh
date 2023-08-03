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
	    cmake \
            git \
            pacman-contrib \
            python-pip


# 3. Install some Python (etc.) packages system-wide (better runtime performance)
pacman --noconfirm \
    -S \
        jdk11-openjdk \
        python-fiona \
        python-geopandas \
        python-joblib \
        python-pyproj \
        python-requests \
        python-shapely \
        vim

# 3½. Install GDAL’s dependencies, so it does not spam the console
# (cf. https://bugs.archlinux.org/index.php?do=details&task_id=75749 )
pacman --noconfirm \
    -S \
        --asdeps \
            arrow \
            cfitsio \
            hdf5 \
            libheif \
            libjxl \
            libwebp \
            mariadb-libs \
            netcdf \
            openexr \
            openjpeg2 \
            podofo-0.9 \
            poppler \
            postgresql-libs


# 4. Create a user to compile additional packages, allow it to run `sudo pacman`
useradd --create-home aurbuilder
echo "aurbuilder ALL=(ALL) NOPASSWD: ALL" >/etc/sudoers.d/10-aurbuilder


# 5. Install dependencies from the AUR
echo 'MAKEFLAGS="-j$(nproc)"' >> /etc/makepkg.conf
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


# 99. Clean-up: remove ourselves
rm -v -- "${BASH_SOURCE[0]}"
