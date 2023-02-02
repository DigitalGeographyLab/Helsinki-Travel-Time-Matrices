FROM alpine:latest

# install dependencies: 
# needs to be in one single RUN command, otherwise ’docker build’ creates
# multiple layers, using diskspace that cannot be freed up by subsequent
# uninstalling ...
#
# the ‘echo >/dev/null’ directives are used as comments; normal comments
# would prevent escaping the line feed
RUN \
    echo "install basic dependencies of r5py/R5/Python packages" >/dev/null \
&& \
    apk add \
        bash \
        gdal \
        geos \
        openjdk17-jdk \
        openjdk17-jre-headless \
        py3-pip \
        python3 \
&& \
    echo "install build dependencies (removed further down)" >/dev/null \
&& \
    apk add \
        g++ \
        gcc \
        gdal-dev \
        geos-dev \
        gfortran \
        linux-headers \
        musl-dev \
        proj-dev \
        proj-util \
        python3-dev \
&& \
    echo "install r5py + python dependencies" >/dev/null \
&& \
    pip install -U r5py \
&& \
    echo "remove build dependencies" \
&& \
    apk del \
        g++ \
        gcc \
        gdal-dev \
        geos-dev \
        gfortran \
        linux-headers \
        musl-dev \
        proj-dev \
        proj-util \
        python3-dev \
&& \
    echo "clear cached package metadata" >/dev/null \
&& \
    apk cache clean || true \
&& \
    pip cache purge \
&& \
    rm -Rf /var/cache/apk/*


# copy our custom R5 build to the image
#ADD https://github.com/DigitalGeographyLab/r5/releases/download/v6.8/r5-v6.8-all.jar /usr/share/java/r5/r5-all.jar
ADD https://github.com/conveyal/r5/releases/download/v6.8/r5-v6.8-all.jar /usr/share/java/r5/r5-all.jar
RUN chmod 0755 /usr/share/java/r5/r5-all.jar


# create a non-root user, make it own the /data directory, set it as default user
ENV USER=dgl
RUN adduser --system --no-create-home "${USER}"
RUN mkdir /data && chown "${USER}" /data
USER "${USER}"


# what to run (bash here is just a placeholder, for now)
ENTRYPOINT ["/bin/bash", "--login"]
#CMD ["/bin/bash", "--login"]
