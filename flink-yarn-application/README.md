# Overview

This example shows how to use `DerivedFeatureView` to backfill the input dataset
with extra features for offline training. It involves the following steps:

1. Read a batch of historical purchase events from a file.

   Each purchase event has the following fields:
   - user_id, unique identifier of the user that made the purchase.
   - item_id, unique identifier of the item that is purchased.
   - item_count, number of items purchased.
   - timestamp, time when this purchase is made.

2. Read a batch of historical item price events from a file.

   Each item price event has the following fields:
   - item_id, unique identifier of the item.
   - price, the new price of this item.
   - timestamp, time when the new price is used for this item.

3. For each purchase event, append the following two fields by joining with item
   price events and performing over-window aggregation, with point-in-time
   correctness in both operations.

   - price, price of the item at the time this purchase is made.
   - total_payment_last_two_minutes, total cost of purchases made by this
     user in a 2-minute window that ends at the time this purchase is made.

4. Output the batch of purchase events backfilled with the extra features to a
   file.

The example demonstrate how to submit the Feathub job to a Yarn cluster in Flink 
application mode.

# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-yarn-application`
folder to run this example.

1. Start Yarn cluster
   
   ```bash
   # If you cannot ssh to localhost without a passphrase, execute the following commands
   $ ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
   $ cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
   $ chmod 0600 ~/.ssh/authorized_keys
   
   $ curl -LO https://archive.apache.org/dist/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz
   $ tar -xzf hadoop-3.3.6.tar.gz --exclude='hadoop-3.3.6/share/doc/**' --exclude='hadoop-3.3.6/share/tools/lib/**'
   $ cp -r etc/hadoop hadoop-3.3.6/etc
   $ ./hadoop-3.3.6/bin/hdfs namenode -format
   $ ./hadoop-3.3.6/sbin/start-dfs.sh
   $ ./hadoop-3.3.6/sbin/start-yarn.sh
   ```
   
   After the Hadoop cluster has started, you should be able to navigate to the
   web UI at [localhost:8088](http://localhost:8088) to view the Hadoop dashboard.
   
2. Prepare Python Virtual Environment

   ```bash
   $ pip install virtualenv
   $ python -m virtualenv venv
   $ source venv/bin/activate
   $ pip install "feathub-nightly[flink]"
   $ deactivate
   $ zip -r venv.zip venv
   $ ./hadoop-3.3.6/bin/hdfs dfs -put venv.zip /venv.zip
   $ rm -rf venv venv.zip
   $ ./hadoop-3.3.6/bin/hdfs dfs -put data /data
   $ ./hadoop-3.3.6/bin/hdfs dfs -put code /code
   ```

3. Submit the Feathub job to Yarn cluster

   ```bash
   $ curl -LO https://archive.apache.org/dist/flink/flink-1.16.2/flink-1.16.2-bin-scala_2.12.tgz
   $ tar -xzf flink-1.16.2-bin-scala_2.12.tgz
   $ export HADOOP_CLASSPATH=`hadoop-3.3.6/bin/hadoop classpath`
   $ ./flink-1.16.2/bin/flink run-application \
       -t yarn-application \
       -Dyarn.application.name=feathub_job \
       -pyarch hdfs:///venv.zip \
       -pyclientexec venv.zip/venv/bin/python3 \
       -pyexec venv.zip/venv/bin/python3 \
       -pyfs hdfs:///code \
       -pym main
   ```
   
   Once the job is submitted, you can list the Yarn application with the follow command:

   ```bash
   $ ./hadoop-3.3.6/bin/yarn app -list
   ```

4. Checkout the outputs.

   ```bash
   $ ./hadoop-3.3.6/bin/hdfs dfs -get /data/output.json data/output.json
   ```

   The file should contain the following rows:

   ```
   user_1,item_1,1,"2022-01-01 00:00:00",user_1item_1,100.0,100.0
   user_1,item_2,2,"2022-01-01 00:01:00",user_1item_2,200.0,500.0
   user_1,item_1,3,"2022-01-01 00:02:00",user_1item_1,200.0,1100.0
   user_2,item_1,1,"2022-01-01 00:03:00",user_2item_1,300.0,300.0
   user_1,item_3,2,"2022-01-01 00:04:00",user_1item_3,300.0,1200.0
   ```

5. Tear down the Yarn cluster.

   ```bash
   $ ./hadoop-3.3.6/sbin/stop-yarn.sh
   $ ./hadoop-3.3.6/sbin/stop-dfs.sh
   ```
