# Overview

This example shows how to use `SqlFeatureView` to clean the input dataset and
generate features. It involves the following steps:

1. Read a batch of historical purchase events from a file.

   Each purchase event has the following fields:
   - user_id, unique identifier of the user that made the purchase.
   - item_id, unique identifier of the item that is purchased.
   - item_count, number of items purchased.
   - item_price, the price of the item when it is purchased.
   - timestamp, time when this purchase is made.

3. Check the format of the input purchase events and filter out invalid entries.
   A valid purchase event is supposed to meet the following requirements.

   - user_id and item_id should not be null.
   - item_id should be a combination of the string "item_" and a number.
   - item_count should be a positive integer.

3. For each purchase event, organize the values in each column with the
   following transformations.

   - convert user_id and item_id into lower-case strings.
   - create total_amount column from the product of item_count and item_price.
   - convert timestamp column into unix timestamp in seconds.

4. Output the batch of the cleaned purchase events to a file.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-derived-feature-view`
folder to run this example.

1. Install Feathub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[flink]"
   ```

2. Start the Flink cluster.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink cluster has started, you should be able to navigate to the
   web UI at [localhost:8081](http://localhost:8081) to view the Flink
   dashboard.

3. Run the FeatHub program to compute and output the extended purchase events to
   a file.

   ```bash
   $ python main.py
   ```

4. Checkout the outputs.

   ```bash
   $ cat data/output.json/*
   ```

   The file should contain the following rows:

   ```
   user_1,item_1,1,100.0,100.0,1640966400
   user_1,item_2,2,200.0,400.0,1640966460
   user_1,item_1,3,300.0,900.0,1640966520
   user_2,item_1,1,400.0,400.0,1640966580
   user_1,item_3,2,200.0,400.0,1640966640
   ```

5. Tear down the Flink cluster after the FeatHub program has finished.

   ```bash
   docker-compose down
   ```
