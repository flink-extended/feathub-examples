# Overview

This example shows how to make the Feathub job fault-tolerant when running with 
FlinkProcessor.

# Prerequisites

Prerequisites for running this example:
- Unix-like operating system (e.g. Linux, Mac OS X)
- Python 3.7
- Docker Compose >= 20.10

# Step-By-Step Instructions

Please execute the following commands under the `flink-fault-tolerance`
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

3. Produce the first series of events into the Kafka topic.

   ```bash
   $ python initialize_kafka_topic.py purchase_events.json
   ```

4. Run the FeatHub program to compute and output the real-time feature to a
   Kafka topic.

   ```bash
   $ python main.py
   ```
   
   Download Kafka consumer and read events from the output topic.

   ```bash
   $ curl -LO https://archive.apache.org/dist/kafka/3.2.3/kafka_2.12-3.2.3.tgz
   $ tar -xzf kafka_2.12-3.2.3.tgz
   $ ./kafka_2.12-3.2.3/bin/kafka-console-consumer.sh \
       --bootstrap-server localhost:9093 \
       --topic user_online_features \
       --from-beginning
   ```
   
   The Kafka topic should contain the following messages:

   ```
   {"user_id":1,"window_time":1640966459999,"total_item_last_two_minutes":1}
   {"user_id":1,"window_time":1640966519999,"total_item_last_two_minutes":3}
   {"user_id":1,"window_time":1640966579999,"total_item_last_two_minutes":5}
   {"user_id":1,"window_time":1640966639999,"total_item_last_two_minutes":3}
   {"user_id":2,"window_time":1640966639999,"total_item_last_two_minutes":1}
   ```

5. Trigger fail-over manually and checkout the final outputs.
   
   While the job is running, you can trigger fail-over by restarting the taskmanager
   
   ```bash
   $ docker-compose restart taskmanager
   ```
   
   Produce the second series of events into the Kafka topic

   ```bash
   $ python initialize_kafka_topic.py purchase_events_2.json
   ```
   
   Read events from the output topic.

   ```bash
   $ ./kafka_2.12-3.2.3/bin/kafka-console-consumer.sh \
       --bootstrap-server localhost:9093 \
       --topic user_online_features \
       --from-beginning
   ```
   
   The Kafka topic should contain the following messages:

   ```
   {"user_id":1,"window_time":1640966459999,"total_item_last_two_minutes":1}
   {"user_id":1,"window_time":1640966519999,"total_item_last_two_minutes":3}
   {"user_id":1,"window_time":1640966579999,"total_item_last_two_minutes":5}
   {"user_id":1,"window_time":1640966639999,"total_item_last_two_minutes":3}
   {"user_id":2,"window_time":1640966639999,"total_item_last_two_minutes":1}
   {"user_id":1,"window_time":1640966699999,"total_item_last_two_minutes":2}
   {"user_id":1,"window_time":1640966759999,"total_item_last_two_minutes":3}
   {"user_id":2,"window_time":1640966759999,"total_item_last_two_minutes":0}
   {"user_id":1,"window_time":1640966879999,"total_item_last_two_minutes":5}
   {"user_id":1,"window_time":1640966939999,"total_item_last_two_minutes":3}
   {"user_id":2,"window_time":1640966939999,"total_item_last_two_minutes":1}
   ```

6. Tear down the Flink and the Kafka clusters after the FeatHub program has
   finished.

   ```bash
   docker-compose down
   ```
