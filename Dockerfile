FROM archlinux AS base

# install r5py, its dependencies, and other required software
COPY python-packages/ /tmp/python-packages/
COPY scripts/prepare-system.sh /tmp/prepare-system.sh
RUN /tmp/prepare-system.sh



FROM base AS r5-and-user

# copy our custom R5 build to the image
ADD https://github.com/conveyal/r5/releases/download/v6.8/r5-v6.8-all.jar /usr/share/java/r5/r5-all.jar
RUN chmod 0755 /usr/share/java/r5/r5-all.jar

# use a non-root user, make it own the /data directory
ENV USER=dgl
RUN mkdir /data && chown "${USER}" /data
USER "${USER}"


FROM r5-and-user AS final-stage

# create a clean single-stage image
COPY --from=r5-and-user / /

# what to run
ENTRYPOINT ["/bin/bash", "--login"]
#CMD ["/bin/bash", "--login"]
