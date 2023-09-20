FROM flink:1.16.1-java8

# The target FeatHub Python package to build the image with.
# It could be a URL to a Feathub Python wheel file or a package on Pypi.
# If it is a package, it should include the flink submodule.
# Valid input examples are as follows.
# - feathub-nightly[flink] (default value)
# - feathub[flink]==0.1.0
# - https://github.com/alibaba/feathub/releases/download/release-0.1.0-rc1/feathub-0.1.0-py3-none-any.whl
ARG FEATHUB_PACKAGE=feathub-nightly[flink]

ENV HADOOP_VERSION=3.1.2
ENV PATH=/opt/hadoop-$HADOOP_VERSION/bin/:$PATH

# Download and configure hadoop binary
WORKDIR /opt
RUN curl -O https://archive.apache.org/dist/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzvf hadoop-$HADOOP_VERSION.tar.gz
RUN echo "export HADOOP_CLASSPATH=`hadoop classpath`" >> ~/.bashrc

# Install flink plugins
WORKDIR ${FLINK_HOME}
RUN mkdir plugins/oss-fs-hadoop && \
    mkdir plugins/s3-fs-hadoop && \
    ln -s ../../opt/flink-oss-fs-hadoop-1.16.1.jar plugins/oss-fs-hadoop/flink-oss-fs-hadoop-1.16.1.jar && \
    ln -s ../../opt/flink-s3-fs-hadoop-1.16.1.jar plugins/s3-fs-hadoop/flink-s3-fs-hadoop-1.16.1.jar

# Install python3.7. This is because flink:1.16.1 docker image has been upgraded to use Debian 11 which
# uses Python 3.9. But PyFlink only supports Python 3.6, 3.7 and 3.8.
RUN apt-get update -y && \
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev liblzma-dev && \
wget https://www.python.org/ftp/python/3.7.9/Python-3.7.9.tgz && \
tar -xvf Python-3.7.9.tgz && \
cd Python-3.7.9 && \
./configure --without-tests --enable-shared && \
make -j6 && \
make install && \
ldconfig /usr/local/lib && \
cd .. && rm -f Python-3.7.9.tgz && rm -rf Python-3.7.9 && \
ln -s /usr/local/bin/python3 /usr/local/bin/python && \
apt-get clean && \
rm -rf /var/lib/apt/lists/*

# Install FeatHub with FlinkProcessor dependencies
COPY install_feathub_with_flink.sh /opt/install_feathub_with_flink.sh
RUN bash /opt/install_feathub_with_flink.sh $FEATHUB_PACKAGE

# Further customization can be added.
# You can refer to https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/docker/#further-customization.
