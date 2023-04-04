# Overview

This example shows how to use `DerivedFeatureView` to backfill the input dataset
with extra features for offline training. It involves the following steps:

1. Read a batch of historical purchase events from a file.

   Each purchase event has the following fields:
   - user_id, unique identifier of the user that made the purchase.
   - item_id, unique identifier of the item that is purchased.
   - item_count, number of items purcahsed.
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


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)

# Step-By-Step Instructions

Please execute the following commands under the `spark-derived-feature-view`
folder to run this example.

1. Install FeatHub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[spark]"
   ```

2. Start the Spark cluster.

   ```bash
   $ docker-compose up -d
   ```

   After the Spark cluster has started, you should be able to navigate to the
   web UI at [localhost:8080](http://localhost:8080) to view the Spark dashboard.

3. As Spark requires access to data files on both the driver and cluster, we 
   need to copy the data files to the same path in the container in advance.

   ```bash
   $ cp -r data /tmp/feathub-data
   ```


4. Run the FeatHub program to compute and output the extended purchase events to
   a file.

   ```bash
   $ python3 main.py
   ```

5. Checkout the outputs.

   ```bash
   $ cat data/output.json/_temporary/0/*/*
   ```

   The file should contain the following rows:

   ```
   user_1,item_1,1,2022-01-01 00:00:00,100.0,100.0
   user_1,item_2,2,2022-01-01 00:01:00,200.0,500.0
   user_1,item_1,3,2022-01-01 00:02:00,200.0,1100.0
   user_2,item_1,1,2022-01-01 00:03:00,300.0,300.0
   user_1,item_3,2,2022-01-01 00:04:00,300.0,1200.0
   ```

6. Tear down the Spark cluster after the FeatHub program has finished.

   ```bash
   docker-compose down
   ```
