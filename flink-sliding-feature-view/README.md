# Overview

This example shows how to use `SlidingFeatureView` to process two streams of
real-time events from two Kafka topics into real-time per-user features and
output those real-time features to another Kafka topic. It involves the
following steps:

1. Read a stream of real-time purchase events from a Kafka topic.

   Each purchase event has the following fields:
   - user_id, unique identifier of the user that made the purchase.
   - item_id, unique identifier of the item that is purchased.
   - item_count, number of items purchased.
   - timestamp, time when this purchase is made.

2. Read a stream of real-time item price events from a Kafka topic.

   Each item price event has the following fields:
   - item_id, unique identifier of the item.
   - price, the new price of this item.
   - timestamp, time when the new price is used for this item.

3. Compute a real-time sliding-window feature and output this feature to a Kafka
   topic.

   For each user_id observed in the purchase events, we would like to maintain
   the total cost of purchases made by this user in a 2-minute sliding window with
   1-minute step size.  We would need to join the purchase event stream with the
   price field from the price event stream before performing sliding-window
   aggregation, with point-in-time correctness in both operations.

   For each user with recently observed purchase, an event should be emitted
   every minute until there is no more purchase event captured in the window for
   this user. Since this feature is computed by a SlidingFeatureView, the number of
   output events might not equal the number events in either input streams.

   Each event in the output Kafka topic has the following fields:
   - user_id, unique identifier of the user.
   - total_payment_last_two_minutes, total cost of purchases made by this user
     in a 2-minute window.
   - timestamp, the end time of the window represented by this event.


# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7
- Docker Compose >= 20.10

# Step-By-Step Instructions

Please execute the following commands under the `flink-sliding-feature-view`
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

3. Producer events into the two Kafka topics.

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
   $ curl -LO https://downloads.apache.org/kafka/3.2.3/kafka_2.12-3.2.3.tgz
   $ tar -xzf kafka_2.12-3.2.3.tgz
   $ ./kafka_2.12-3.2.3/bin/kafka-console-consumer.sh \
       --bootstrap-server localhost:9093 \
       --topic user_online_features \
       --from-beginning
   ```

   The Kafka topic should contain the following messages:

   ```
   {"user_id":"user_1","window_time":1640966459999,"total_payment_last_two_minutes":100.0}
   {"user_id":"user_1","window_time":1640966519999,"total_payment_last_two_minutes":500.0}
   {"user_id":"user_1","window_time":1640966579999,"total_payment_last_two_minutes":1000.0}
   {"user_id":"user_2","window_time":1640966639999,"total_payment_last_two_minutes":300.0}
   {"user_id":"user_1","window_time":1640966639999,"total_payment_last_two_minutes":600.0}
   ```

5. Tear down the Flink and the Kafka clusters after the FeatHub program has
   finished.

   Note that since the FeatHub job is reading from Kafka, it will run
   indefinitely, and you would need to manually press Control-C to stop the program.

   ```bash
   docker-compose down
   ```
