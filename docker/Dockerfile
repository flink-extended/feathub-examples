FROM flink:1.15.2

ENV HADOOP_VERSION=3.2.4
ENV PATH=/opt/hadoop-$HADOOP_VERSION/bin/:$PATH

# Downloads and extracts hadoop binary
WORKDIR /opt
RUN curl -O https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzvf hadoop-$HADOOP_VERSION.tar.gz

# Installs flink plugins
WORKDIR ${FLINK_HOME}
RUN mkdir plugins/oss-fs-hadoop && \
    mkdir plugins/s3-fs-hadoop && \
    ln -s ../../opt/flink-oss-fs-hadoop-1.15.2.jar plugins/oss-fs-hadoop/flink-oss-fs-hadoop-1.15.2.jar && \
    ln -s ../../opt/flink-s3-fs-hadoop-1.15.2.jar plugins/s3-fs-hadoop/flink-s3-fs-hadoop-1.15.2.jar

# Further customization can be added.
# You can refer to https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/docker/#further-customization.
