FROM flink:1.15.2

ENV HADOOP_VERSION=3.2.4

#Prepare hadoop
WORKDIR /opt
RUN curl -O https://dlcdn.apache.org/hadoop/common/hadoop-$HADOOP_VERSION/hadoop-$HADOOP_VERSION.tar.gz && \
    tar -xzvf hadoop-$HADOOP_VERSION.tar.gz

ENV PATH=/opt/hadoop-$HADOOP_VERSION/bin/:$PATH

# Prepare flink
WORKDIR ${FLINK_HOME}
RUN mkdir plugins/oss-fs-hadoop && \
    mkdir plugins/s3-fs-hadoop && \
    ln -s ../../opt/$(ls opt | grep oss-fs-hadoop) plugins/oss-fs-hadoop/$(ls opt | grep oss-fs-hadoop) && \
    ln -s ../../opt/$(ls opt | grep s3-fs-hadoop) plugins/s3-fs-hadoop/$(ls opt | grep s3-fs-hadoop)

# Further customization can be added.
# You can refer to https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/docker/#further-customization.
