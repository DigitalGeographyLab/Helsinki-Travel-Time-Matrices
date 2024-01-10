FROM ubuntu:22.04 AS base

# directory for installation scripts
RUN mkdir /tmp/scripts

# install base system + dependencies for r5py
COPY scripts/10-base-system.sh /tmp/scripts/
RUN /tmp/scripts/10-base-system.sh

# install r5py and test it
FROM base AS base_r5py
COPY scripts/20-install-and-test-r5py.sh /tmp/scripts/
RUN /tmp/scripts/20-install-and-test-r5py.sh

# install the local python packages
FROM base_r5py AS base_r5py_local_python_packages
COPY scripts/30-install-local-python-packages.sh /tmp/scripts/
RUN /tmp/scripts/30-install-local-python-packages.sh

# clean up system image
FROM base_r5py_local_python_packages AS system
COPY scripts/99-cleanup.sh /tmp/scripts/
RUN /tmp/scripts/99-cleanup.sh


FROM system AS dgl-user

# use a non-root user, make it own the /data directory
ENV USER=dgl
RUN mkdir /data && chown "${USER}" /data
RUN mkdir -p /home/dgl/.config && chown "${USER}" -R /data
COPY r5py.yml /home/dgl/.config/r5py.yml
USER "${USER}"


FROM dgl-user AS final-stage

# create a clean single-stage image
COPY --from=dgl-user / /

# what to run
ENTRYPOINT ["/home/dgl/.local/bin/travel-time-matrix"]
#ENTRYPOINT ["/bin/bash", "--login"]
