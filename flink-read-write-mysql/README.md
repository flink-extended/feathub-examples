# Overview

This example shows how to save input dataset with features into a MySQL Cluster
with `MySQLSink`, and provides online serving based on the saved features with
`MySQLSource`. It involves the following steps:

1. Read a batch of historical item price events from a file.

   Each item price event has the following fields:
   - item_id, unique identifier of the item.
   - price, the new price of this item.
   - timestamp, time when the new price is used for this item.

2. For each item price event, save the event into a MySQL cluster. If a feature
   with the same item_id has been saved to MySQL before，FeatHub will update the price
   and timestamp values of the entry in MySQL.

3. Read the latest item prices from the MySQL cluster and use them to create an
   `OnDemandFeatureView` to provide online serving. In this example, the
   features displayed by online serving are printed out in the terminal.

# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-read-write-mysql` folder
to run this example.

1. Install FeatHub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[flink]"
   ```

2. Start the Flink cluster and MySQL cluster.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink cluster has started, you should be able to navigate to the
   web UI at [localhost:8081](http://localhost:8081) to view the Flink
   dashboard.

3. Initialize MySQL Table
   
   ```bash
   $ python initialize_mysql_table.py
   ```

4. Run the FeatHub program to save the item price features to MySQL and provide
   online serving accordingly.

   ```bash
   $ python main.py
   ```

   You should be able to find the following information printed out in the end
   of the terminal.

   ```
     item_id  price
   0  item_1  400.0
   1  item_2  200.0
   2  item_3  300.0
   ```

5. Tear down the Flink cluster and MySQL cluster after the FeatHub program has
   finished.

   ```bash
   docker-compose down
   ```
