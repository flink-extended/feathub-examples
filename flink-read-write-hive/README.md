# Overview

This example shows how to save input dataset with features into a Hive table
with `HiveSink`, and reads out the saved features with `HiveSource`. It involves
the following steps:

1. Read a batch of historical item price events from a file.

   Each item price event has the following fields:
   - item_id, unique identifier of the item.
   - price, the new price of this item.
   - timestamp, time when the new price is used for this item.

2. For each item price event, save the event into a Hive table. As the sink is
   running as a streaming append sink, features with the same item_id would be
   saved as different entries in the Hive table.

3. Read the latest item prices from the Hive table and save them to a local file.

# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)

# Step-By-Step Instructions

Please execute the following commands under the `flink-read-write-hive` folder
to run this example.

1. Build the Flink image to support Hive.

   ```bash
   $ docker build --rm -t feathub-flink -f ../docker/Dockerfile .
   ```

2. Download Flink's bundled hive jar to the `flink-read-write-hive` folder.
   
   ```bash
   $ wget https://repo.maven.apache.org/maven2/org/apache/flink/flink-sql-connector-hive-3.1.2_2.12/1.16.1/flink-sql-connector-hive-3.1.2_2.12-1.16.1.jar
   ```

3. Start the Flink cluster and Hive service.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink cluster has started, you should be able to navigate to the
   web UI at [localhost:8081](http://localhost:8081) to view the Flink
   dashboard.

4. Run the FeatHub program from inside the container to save the item price
   features to Hive and reads them out.

   ```bash
   $ docker exec -w /root/flink-read-write-hive flink bash -c "export HADOOP_CLASSPATH=\`hadoop classpath\`; python main.py"
   ```

   The program would create and submit two Flink jobs, and The second job reads 
   Hive table as an unbounded stream and runs continuously until it is 
   explicitly cancelled. You may open a second terminal and execute the
   following command to check the results saved in local file.

   ```
   cat data/output/.part-*
   ```

   You should be able to find the following information printed out in the
   terminal.

   ```
   item_1,100.0,"2022-01-01 00:00:00 +0800"
   item_2,200.0,"2022-01-01 00:00:00 +0800"
   item_3,300.0,"2022-01-01 00:00:00 +0800"
   item_1,200.0,"2022-01-01 00:01:30 +0800"
   item_1,300.0,"2022-01-01 00:02:30 +0800"
   item_1,400.0,"2022-01-01 00:03:30 +0800"
   ```

5. Press Control-C to stop the program and tear down the Flink cluster and
   Hive cluster after the FeatHub program has finished.

   ```bash
   docker-compose down
   ```
