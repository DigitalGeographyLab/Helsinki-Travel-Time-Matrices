FROM archlinux AS base

ENV R5_JAR_URL=https://github.com/DigitalGeographyLab/r5/releases/download/v6.9-post12-g8ebe6ff-dgl-20230330/r5-v6.9-12-g8ebe6ff-all.jar

# install r5py, its dependencies, and other required software
COPY python-packages/ /tmp/python-packages/
COPY scripts/prepare-system.sh /tmp/prepare-system.sh
RUN /tmp/prepare-system.sh



FROM base AS r5-and-user

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
