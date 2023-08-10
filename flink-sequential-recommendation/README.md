# Overview

This example shows how to generate sequence feature using FeatHub's
`COLLECT_LIST` aggregation function. It involves the following steps:

1. Read a stream of real-time browse events from a Kafka topic.

   Each browse event has the following fields:
   - user_id, unique identifier of a user.
   - item_id, unique identifier of the item that is browsed by the user.
   - event_type, the type of the event, e.g., click, exposure.
   - timestamp, time when this purchase is made.

2. For each event received from Kafka, computes and appends an extra feature
   which shows a list of last 10 item that the given user has clicked. This
   aggregation computation is achieved using OverWindowTransform.

3. Output the user_id and aggregation result to a Redis service.

4. Getting the final online aggregation features from Redis.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the
`flink-sequential-recommendation` folder to run this example.

1. Install FeatHub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[flink]"
   ```

2. Start the Flink, Kafka and Redis clusters.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink cluster has started, you should be able to navigate to the
   web UI at [localhost:8081](http://localhost:8081) to view the Flink
   dashboard.

3. Produce events into the Kafka topic.

   ```bash
   $ python initialize_kafka_topic.py
   ```

4. Run the FeatHub program to compute and output the browse history to Redis.

   ```bash
   $ python main.py
   ```
   
   You should find the following contents printed out to the terminal.

   ```
      user_id click_history
   0        1  [1, 3, 5, 4]
   1        2        [4, 2]
   2        3        [3, 2]
   ```

5. Tear down the Flink, Kafka and Redis clusters after the FeatHub program has
   finished.

   ```bash
   docker-compose down
   ```
