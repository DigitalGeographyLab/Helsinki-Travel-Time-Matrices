FROM archlinux AS base

ENV R5_JAR_URL=https://github.com/DigitalGeographyLab/r5/releases/download/v6.9-post13-gc0b53c6-dgl-20230428/r5-v6.9-post13-gc0b53c6-dgl-20230428-all.jar

# copy installation scripts
COPY scripts/ /tmp/scripts/

# install base system + dependencies for r5py
RUN /tmp/scripts/10-base-system.sh

# install r5py and test it
FROM base AS base_r5py
RUN /tmp/scripts/20-install-and-test-r5py.sh

# install the local python packages
FROM base_r5py AS base_r5py_local_python_packages
COPY python-packages/ /tmp/python-packages/
RUN /tmp/scripts/30-install-local-python-packages.sh

# clean up system image
FROM base_r5py_local_python_packages AS system
RUN /tmp/scripts/99-cleanup.sh


FROM system AS r5-and-user

# copy our custom R5 build to the image
ADD "${R5_JAR_URL}" /usr/share/java/r5/r5-all.jar
RUN chmod 0755 /usr/share/java/r5/r5-all.jar

# use a non-root user, make it own the /data directory
ENV USER=dgl
RUN mkdir /data && chown "${USER}" /data
USER "${USER}"


FROM r5-and-user AS final-stage

# create a clean single-stage image
COPY --from=r5-and-user / /

# what to run
ENTRYPOINT ["/home/dgl/.local/bin/travel-time-matrix"]
#ENTRYPOINT ["/bin/bash", "--login"]
