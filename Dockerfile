FROM alpine:edge

# install dependencies: 
# needs to be in one single RUN command, otherwise ’docker build’ creates
# multiple layers, using diskspace that cannot be freed up by subsequent
# uninstalling ...
#
# the ‘echo >/dev/null’ directives are used as comments; normal comments
# would prevent escaping the line feed
RUN \
    cat /etc/apk/repositories \
&& \
    echo "enable community and testing repositories" >/dev/null \
&& \
    sed 's/^#\(.*(community|testing)\)$/\1/' -i /etc/apk/repositories \
&& \
    echo "https://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories \
&& \
    echo "install basic dependencies of r5py/R5/Python packages" >/dev/null \
&& \
    apk add \
        bash \
        gdal \
        geos \
        libosmium \
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
        git \
        libosmium-dev \
        linux-headers \
        musl-dev \
        proj-dev \
        proj-util \
        python3-dev \
&& \
    echo "install r5py + python dependencies" >/dev/null \
&& \
    pip install -U git+https://github.com/r5py/r5py.git \
&& \
    echo "remove build dependencies" \
&& \
    apk del \
        g++ \
        gcc \
        gdal-dev \
        geos-dev \
        gfortran \
        git \
        libosmium-dev \
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


# set Java environment variables
ENV JAVA_HOME="/usr/lib/jvm/default-jvm"
ENV LD_LIBRARY_PATH="/usr/lib:/usr/lib/jvm/default-jvm/lib/server/:/usr/lib/jvm/default-jvm/lib/"
#PATH=$PATH:/usr/lib/jvm/default-jvm/bin


# copy our custom R5 build to the image
ADD https://github-registry-files.githubusercontent.com/592682991/0945a580-bbfe-11ed-895a-86b05cce21cd?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20230306%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20230306T093453Z&X-Amz-Expires=300&X-Amz-Signature=87c71826d0e70278f4320f1a74e4a5e5b37d860735545341625f589d6ec37e70&X-Amz-SignedHeaders=host&actor_id=0&key_id=0&repo_id=592682991&response-content-disposition=filename%3Dr5-v6.9-8-g739d60a-all.jar&response-content-type=application%2Foctet-stream /usr/share/java/r5/r5-all.jar
#ADD https://github.com/conveyal/r5/releases/download/v6.8/r5-v6.8-all.jar /usr/share/java/r5/r5-all.jar
RUN chmod 0755 /usr/share/java/r5/r5-all.jar


# create a non-root user, make it own the /data directory, set it as default user
ENV USER=dgl
RUN adduser --system --no-create-home "${USER}"
RUN mkdir /data && chown "${USER}" /data
USER "${USER}"


# what to run (bash here is just a placeholder, for now)
ENTRYPOINT ["/bin/bash", "--login"]
#CMD ["/bin/bash", "--login"]
