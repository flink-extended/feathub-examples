FROM flink:1.15.2

ENV HADOOP_VERSION=3.2.4
ENV PATH=/opt/hadoop-$HADOOP_VERSION/bin/:$PATH

# Download and extract hadoop binary
WORKDIR /opt
RUN curl -O https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzvf hadoop-$HADOOP_VERSION.tar.gz

# Install flink plugins
WORKDIR ${FLINK_HOME}
RUN mkdir plugins/oss-fs-hadoop && \
    mkdir plugins/s3-fs-hadoop && \
    ln -s ../../opt/flink-oss-fs-hadoop-1.15.2.jar plugins/oss-fs-hadoop/flink-oss-fs-hadoop-1.15.2.jar && \
    ln -s ../../opt/flink-s3-fs-hadoop-1.15.2.jar plugins/s3-fs-hadoop/flink-s3-fs-hadoop-1.15.2.jar

# Install python3.7. This is because flink:1.15.2 docker image has been upgraded to use Debian 11 which
# uses Python 3.9. But PyFlink only supports Python 3.6, 3.7 and 3.8.
RUN apt-get update -y && \
apt-get install -y build-essential libssl-dev zlib1g-dev libbz2-dev libffi-dev && \
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
RUN pip3 install feathub-nightly[flink]

# Further customization can be added.
# You can refer to https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/docker/#further-customization.
