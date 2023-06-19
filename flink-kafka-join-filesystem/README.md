# Overview

This example shows how to use `DerivedFeatureView` to enrich the user behavior event
from Kafka with the item attributes from FileSystem. It involves the following steps:

1. Read a stream of real-time user behavior events from a Kafka topic.

   Each event has the following fields:
   - user_id, unique identifier of the user.
   - item_id, unique identifier of the item.
   - type, the type of the behavior, e.g., click, exposure.
   - timestamp, time when this behavior is made.

2. Read a batch of item attributes from a file.

   Each item has the following fields:
   - item_id, unique identifier of the item.
   - brand, the brand of this item.
   - category, the category of the item.
   - timestamp, time when the item is created or updated.

3. Enrich the user activity events by joining the items' attributes from a file.

4. Output the enriched user activity events to a Kafka topic.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7

# Step-By-Step Instructions

Please execute the following commands under the `flink-kafka-join-filesystem`
folder to run this example.

1. Install FeatHub pip package with FlinkProcessor dependencies.

   ```bash
   $ python -m pip install --upgrade "feathub-nightly[flink]"
   ```

2. Start the Flink and the Kafka cluster.

   ```bash
   $ docker-compose up -d
   ```

   After the Flink and the Kafka clusters have started, you should be able to
   navigate to the web UI at [localhost:8081](http://localhost:8081) to view the
   Flink dashboard.

3. Produce events into the two Kafka topics.

   ```bash
   $ python initialize_kafka_topic.py
   ```

4. Run the FeatHub program to compute and output the real-time feature to a
   Kafka topic.

   ```bash
   $ python main.py
   ```

5. Checkout the outputs.

   Download Kafka consumer and read events from the output topic.

   ```bash
   $ curl -LO https://archive.apache.org/dist/kafka/3.2.3/kafka_2.12-3.2.3.tgz
   $ tar -xzf kafka_2.12-3.2.3.tgz
   $ ./kafka_2.12-3.2.3/bin/kafka-console-consumer.sh \
       --bootstrap-server localhost:9093 \
       --topic enriched_user_behavior_events \
       --from-beginning
   ```

   The Kafka topic should contain the following messages:

   ```
   {"user_id":"u6","item_id":"i1","action_type":"exposure","timestamp":1684484065,"brand":"brand1"}
   {"user_id":"u1","item_id":"i9","action_type":"click","timestamp":1684484069,"brand":"brand3"}
   {"user_id":"u10","item_id":"i2","action_type":"exposure","timestamp":1684484066,"brand":"brand1"}
   {"user_id":"u4","item_id":"i4","action_type":"exposure","timestamp":1684484067,"brand":"brand2"}
   {"user_id":"u9","item_id":"i7","action_type":"exposure","timestamp":1684484068,"brand":"brand3"}
   {"user_id":"u9","item_id":"i6","action_type":"exposure","timestamp":1684484068,"brand":"brand2"}
   {"user_id":"u6","item_id":"i5","action_type":"exposure","timestamp":1684484067,"brand":"brand2"}
   {"user_id":"u5","item_id":"i8","action_type":"exposure","timestamp":1684484069,"brand":"brand3"}
   {"user_id":"u3","item_id":"i3","action_type":"exposure","timestamp":1684484066,"brand":"brand1"}
   {"user_id":"u4","item_id":"i10","action_type":"exposure","timestamp":1684484070,"brand":"brand3"}
   ```

6. Tear down the Flink and the Kafka clusters after the FeatHub program has
   finished.

   Note that since the FeatHub job is reading from Kafka, it will run
   indefinitely, and you would need to manually press Control-C to stop the program.

   ```bash
   docker-compose down
   ```
